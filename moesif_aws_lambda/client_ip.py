import re

class ClientIp:

    def is_ip(self, value):
        if not value is None:
            ipv4 = r"^(?:(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.){3}(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])$"
            ipv6 = r"^((?=.*::)(?!.*::.+::)(::)?([\dA-F]{1,4}:(:|\b)|){5}|([\dA-F]{1,4}:){6})((([\dA-F]{1,4}((?!\3)::|:\b|$))|(?!\2\3)){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})$/i"
            return re.match(ipv4, value) or re.match(ipv6, value)

    def getClientIpFromXForwardedFor(self, value):
        try:

            if not value or value is None:
                return None

            if not isinstance(value, str):
                print("Expected a string, got -" + str(type(value)))
            else:
                # x-forwarded-for may return multiple IP addresses in the format:
                # "client IP, proxy 1 IP, proxy 2 IP"
                # Therefore, the right-most IP address is the IP address of the most recent proxy
                # and the left-most IP address is the IP address of the originating client.
                # source: http://docs.aws.amazon.com/elasticloadbalancing/latest/classic/x-forwarded-headers.html
                # Azure Web App's also adds a port for some reason, so we'll only use the first part (the IP)
                forwardedIps = []

                for e in value.split(','):
                    ip = e.strip()
                    if ':' in ip:
                        splitted = ip.split(':')
                        if (len(splitted) == 2):
                            forwardedIps.append(splitted[0])
                    forwardedIps.append(ip)

                # Sometimes IP addresses in this header can be 'unknown' (http://stackoverflow.com/a/11285650).
                # Therefore taking the left-most IP address that is not unknown
                # A Squid configuration directive can also set the value to "unknown" (http://www.squid-cache.org/Doc/config/forwarded_for/)
                return next(item for item in forwardedIps if self.is_ip(item))
        except StopIteration:
            return value.encode('utf-8')

    def get_client_address(self, headers, default_source_ip):
        try:
            # Standard headers used by Amazon EC2, Heroku, and others.
            if 'X-Client-Ip' in headers:
                if self.is_ip(headers['X-Client-Ip']):
                    return headers['X-Client-Ip']

            # Load-balancers (AWS ELB) or proxies.
            if 'X-Forwarded-For' in headers:
                xForwardedFor = self.getClientIpFromXForwardedFor(headers['X-Forwarded-For'])
                if self.is_ip(xForwardedFor):
                    return xForwardedFor

            # Cloudflare.
            # @see https://support.cloudflare.com/hc/en-us/articles/200170986-How-does-Cloudflare-handle-HTTP-Request-headers-
            # CF-Connecting-IP - applied to every request to the origin.
            if 'Cf-Connecting-Ip' in headers:
                if self.is_ip(headers['Cf-Connecting-Ip']):
                    return headers['Cf-Connecting-Ip']

            # Akamai and Cloudflare: True-Client-IP.
            if 'True-Client-Ip' in headers:
                if self.is_ip(headers['True-Client-Ip']):
                    return headers['True-Client-Ip']

            # Default nginx proxy/fcgi; alternative to x-forwarded-for, used by some proxies.
            if 'X-Real-Ip' in headers:
                if self.is_ip(headers['X-Real-Ip']):
                    return headers['X-Real-Ip']

            # (Rackspace LB and Riverbed's Stingray)
            # http://www.rackspace.com/knowledge_center/article/controlling-access-to-linux-cloud-sites-based-on-the-client-ip-address
            # https://splash.riverbed.com/docs/DOC-1926
            if 'X-Cluster-Client-Ip' in headers:
                if self.is_ip(headers['X-Cluster-Client-Ip']):
                    return headers['X-Cluster-Client-Ip']

            if 'X-Forwarded' in headers:
                if self.is_ip(headers['X-Forwarded']):
                    return headers['X-Forwarded']

            if 'Forwarded-For' in headers:
                if self.is_ip(headers['Forwarded-For']):
                    return headers['Forwarded-For']

            if 'Forwarded' in headers:
                if self.is_ip(headers['Forwarded']):
                    return headers['Forwarded']

            if default_source_ip:
                return default_source_ip
            else:
                return None
        except Exception:
            if default_source_ip:
                return default_source_ip
            else:
                return None
