#!/bin/bash
. ./cgi.sh
s=subs/list
u=subs/ulist

# Assuming
# $CGI_id GET + ?id= = one click unsubscribe
# $CGI_email POST = subscribing

subscribe() {
rid=$(head -c 4 /dev/urandom | xxd -p)
echo $rid $(date +%s) $REMOTE_ADDR $CGI_email >> $s
echo $rid
grep -q "$rid" $s || return 1
}

unsubscribe() {
id=$(echo $1 | tr -dc '[:xdigit:]')
test "$id" || return 1
subs=$(grep -m1 -n ^$id $s)
echo $subs | awk '{print $4}'
lineno=$(echo $subs | cut -d: -f1)
if test "$lineno" -gt 0 # test to see if it's a number
then
	# Record when they left and why
	echo $(date +%s) $(echo $subs | awk '{print $3, $4}') $CGI_why >> $u
	# Delete line
	sed -i "${lineno}d" $s
fi
}

cat <<EOF
Content-type: text/html

<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>email list</title>
<style>
$(cat style.css)
</style>
</head>
<body>
EOF

if test $REQUEST_METHOD = "POST" && test "$CGI_email"
then
# code that subscribes
	email=$(echo $CGI_email | tr -dc '[:alnum:].@' | tr '[:upper:]' '[:lower:]')
	id=$(subscribe $email)
	if test $? -eq 1
	then
		echo "<h2>permissions incorrect. chown :www-data $s</h2>"
		exit
	fi
	cat <<EOF
<h3>Thank you for subscribing !</h3>
<form action="/list.cgi" method=get>
<input required=required type=email name=email title="We will never sell or distribute your email address" placeholder="Your email address" value="$email"/>
<input name=id type=hidden value=$id>
<input name=submit type=submit value="Unsubscribe"/>
</form>
<p>
<a href="http://$HTTP_HOST/list/$id">One-click unsubscribe</a>
</p>
</body>
</html>
EOF

else

if test "$CGI_id"
then
	email=$(unsubscribe $CGI_id)
	echo "<h3>We are sorry to see you go $email !</h3>"
fi

cat <<EOF
<form action="/list.cgi" method=post>
<input required=required type=email name=email title="We will never sell or distribute your email address" placeholder="Your email address" value="$email"/>
<input name=submit type=submit value="Subscribe"/>
</form>
EOF
fi