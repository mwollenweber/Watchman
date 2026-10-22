# Production on AWS: scheduled start, self-stop

The daily ingest needs an instance with a lot of memory, and that instance is expensive to keep running. The run itself only takes a few hours, so production keeps the instance stopped and starts it once a day. At boot it runs the daily pipeline, then powers itself off. You pay for compute only while the run is in progress. EBS storage is still billed while the instance is stopped.

This page documents that setup. It uses placeholders (`<ACCOUNT_ID>`, `<INSTANCE_ID>`, `<REGION>`) in place of real identifiers; look those up in the AWS console when you need them.

## How it fits together

```text
EventBridge Scheduler  (cron 0 4 * * ? *, America/New_York)
        │  calls ec2:StartInstances, assuming the scheduler execution role
        ▼
EC2 instance boots
        │  systemd starts watchman-daily.service (oneshot, after network-online)
        ▼
run-daily.sh --shutdown <config>
        │  update_zone → run_searches → run_alerts → purge_new → clean ./tmp
        ▼
shutdown -h now
        │  instance-initiated shutdown behavior = stop
        ▼
Instance is stopped until the next morning
```

There are two halves:

- The instance side is `install-startup.sh --shutdown`, which installs a systemd service that runs `run-daily.sh` on every boot and lets the run user power off the host when it finishes.
- The AWS side is an EventBridge Scheduler schedule that starts the instance every morning through an IAM role allowed to start that one instance and nothing else.

`run-daily.sh` does not stop on errors, so a failed step still ends in a shutdown. A step that hangs does not; see [Known gaps](#known-gaps).

## Instance requirements

- Size the instance for memory. Production runs an r5.2xlarge (64 GiB) on Amazon Linux 2023.
- The instance-initiated shutdown behavior must be `stop`. This is the default for EBS-backed instances. If it is set to `terminate`, the first run deletes the instance. Check it with:

  ```bash
  aws ec2 describe-instance-attribute \
      --instance-id <INSTANCE_ID> \
      --attribute instanceInitiatedShutdownBehavior
  ```

- With the default `install.sh` setup, Postgres and Redis run on the same instance. The database, the Django admin, and the API are only reachable while the instance is up.
- If the EBS volumes are encrypted with a customer managed KMS key, the scheduler role also needs `kms:CreateGrant` on that key. Without it the instance goes to `pending` and then back to `stopped`. Volumes that are unencrypted or use the AWS managed `aws/ebs` key need no extra permissions. See AWS's [KMS permissions for EC2](https://repost.aws/knowledge-center/kms-iam-ec2-permission) article.

## 1. Install the boot service on the instance

Install Watchman as described in the [README](../README.md#install), with production settings in their own config file (for example `prod.rc`). Then install the service with `--shutdown`:

```bash
sudo ./install-startup.sh --shutdown --config prod.rc
```

This creates `watchman-daily.service` and a sudoers rule that lets the run user execute only `shutdown -h now` without a password. Use `--dry-run` first to see exactly what it will write.

Confirm it is enabled:

```bash
systemctl is-enabled watchman-daily
```

## 2. Create the scheduler execution role

EventBridge Scheduler needs a role it can assume to call `StartInstances`. Scope it to the one instance.

Trust policy (`trust.json`). The `aws:SourceAccount` condition keeps Scheduler from assuming the role on behalf of another account:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "scheduler.amazonaws.com" },
      "Action": "sts:AssumeRole",
      "Condition": { "StringEquals": { "aws:SourceAccount": "<ACCOUNT_ID>" } }
    }
  ]
}
```

Permissions policy (`start-watchman-daily.json`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:StartInstances",
      "Resource": "arn:aws:ec2:<REGION>:<ACCOUNT_ID>:instance/<INSTANCE_ID>"
    }
  ]
}
```

Create the role with an inline policy:

```bash
aws iam create-role \
    --role-name watchman-daily-scheduler \
    --assume-role-policy-document file://trust.json
aws iam put-role-policy \
    --role-name watchman-daily-scheduler \
    --policy-name start-watchman-daily \
    --policy-document file://start-watchman-daily.json
```

In the console, this is IAM > Roles > Create role > Custom trust policy, then Create inline policy on the permissions step.

## 3. Create the schedule

| Setting | Value |
| --- | --- |
| Name | `watchman-daily-start` (default schedule group) |
| Schedule | Recurring, cron `0 4 * * ? *` |
| Time zone | `America/New_York` |
| Flexible time window | Off |
| Target | All APIs > Amazon EC2 > `StartInstances` |
| Input | `{"InstanceIds": ["<INSTANCE_ID>"]}` |
| Retry policy | On, max event age 1 hour, 10 attempts |
| Dead-letter queue | None |
| Execution role | `watchman-daily-scheduler` |

The schedule runs in `America/New_York`, so it fires at 04:00 Eastern year-round and Scheduler handles the daylight saving shift. In UTC that is 08:00 during EDT and 09:00 during EST.

The retry policy caps retries at one hour so a transient failure still starts the run near 04:00 instead of hours later. The Scheduler default is to retry for up to 24 hours.

In the console the schedule is under EventBridge > Scheduler > Schedules > Create schedule. The console can't create a role for an "All APIs" (universal) target, so create the role in step 2 first and pick it under "Use existing role".

CLI equivalent:

```bash
aws scheduler create-schedule \
    --region <REGION> \
    --name watchman-daily-start \
    --schedule-expression "cron(0 4 * * ? *)" \
    --schedule-expression-timezone "America/New_York" \
    --flexible-time-window Mode=OFF \
    --target '{
      "Arn": "arn:aws:scheduler:::aws-sdk:ec2:startInstances",
      "RoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/watchman-daily-scheduler",
      "Input": "{\"InstanceIds\": [\"<INSTANCE_ID>\"]}",
      "RetryPolicy": {"MaximumEventAgeInSeconds": 3600, "MaximumRetryAttempts": 10}
    }'
```

## Operating it

Logs from the run are in the journal:

```bash
journalctl -u watchman-daily
```

To read a previous day's run you need a persistent journal (`/var/log/journal` exists). Use `journalctl -u watchman-daily --boot=-1` for the last boot.

To do maintenance without the host powering off, start the instance, log in, and stop the service before the run finishes. This also ends the run in progress:

```bash
sudo systemctl stop watchman-daily
```

To skip runs entirely, disable the schedule in the Scheduler console. Starting the instance by hand still triggers a run and a shutdown.

To change the run time, edit the cron expression on the schedule. Keep the time zone set to `America/New_York`.

To confirm the schedule fired, look for the `StartInstances` event in CloudTrail under the `watchman-daily-scheduler` role, or at the instance's state history in EC2. Scheduler also publishes invocation and error metrics to CloudWatch under the `AWS/Scheduler` namespace.

To remove the setup, delete the schedule, delete the role, and on the instance run `sudo ./install-startup.sh --uninstall`.

## Known gaps

- Nothing bounds the run time. The unit sets `TimeoutStartSec=infinity` because zone updates can take hours, so a hung run keeps the large instance up and billing until someone notices. A second schedule that calls `StopInstances` at a fixed later hour, or a CloudWatch alarm on instance uptime, would cap the cost.
- Nothing alerts when the schedule fails to start the instance. There is no dead-letter queue, and Scheduler errors only show up in CloudWatch metrics.
