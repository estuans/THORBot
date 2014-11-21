
def requires_superuser(aFunc):
    """Requires the user issuing the command to be in the list of superusers."""
    def securedFunc( *args, **kwargs):
        # Collect the args,
        instance = args[0]
        user = args[1]
        channel = args[2]
        msg = args[3]

        user = user.split('!', 1)[0]

        if user in instance.superusers:
            try:
                result= aFunc(*args, **kwargs)
            except Exception, e:
                print "exception", aFunc.__name__, e

                raise
            else:
                return result
        else:
            return instance.msg(channel, "AUTH: %s is not allowed to do that!")
    securedFunc.__name__= aFunc.__name__
    securedFunc.__doc__= aFunc.__doc__
    return securedFunc