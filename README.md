# ndex-python
This repository stores all of the code we are going to release under the name 'ndex' on PyPi.

API documention can be found here: http://ndexbio.github.io/ndex-python/index.html



User

get_user_by_username(username)

Returns the user corresponding to the provided username
Error if this account is not found
If the user account has not been verified by the user yet, the returned object will contain no user UUID and the isVerified field will be false.
