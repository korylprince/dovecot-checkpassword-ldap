dovecot-checkpassword-ldap
<https://github.com/korylprince/dovecot-checkpassword-ldap>

Dovecot's ldap plugin has lots of features, but didn't have everything I needed. This is a python script to be used with the Dovecot Checkpassword interface.

#Usage#

Uses redis as a cache in front of ldap. Make sure to have python-ldap and redis-py installed.

I used this with Active Directory. There's probably things you'd need to change to make it work with something else. Put checkpassword and settings.py somewhere in the same directory then put something like

    passdb {
          driver = checkpassword
          args = /path/to/checkpassword
    }
    userdb {
          driver = prefetch
    }
    userdb {
          driver = checkpassword
          args = /path/to/checkpassword
    }

in your Dovecot config.

If you have any issues or questions (or want to make it better), email the email address below, or open an issue at: <https://github.com/korylprince/dovecot-checkpassword-ldap/issues>

Can't promise anything though.

#Tests#

I wrote some unit tests for this. Edit user.py with a known configuration for a user and run the tests.

Running ```python <test file> time``` will run 20 iterations and give the average time.

#Copyright Information#
Copyright 2013 Kory Prince (korylprince AT gmail DAWT com).

License is the "Do Whatever You Want With It" License. Public Domain - whatever you want.

