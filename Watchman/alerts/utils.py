import dns.resolver


def has_mx(domain):
    try:
        for x in dns.resolver.resolve(domain, 'MX'):
            return True
    except Exception as e:
        return False
    return False


def get_mx(domain):
    mx_records = []
    for x in dns.resolver.resolve(domain, 'MX'):
        mx_records.append(x.to_text())
    return mx_records


def has_website(domain):
    #fixme #todo
    return False
