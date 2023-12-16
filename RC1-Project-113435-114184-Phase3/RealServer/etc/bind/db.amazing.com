$TTL	604800
$ORIGIN amazing.com.
@	IN	SOA	ns1.amazing.com. adm.amazing.com. (
			2	; Serial
			604800	; Refresh
			86400	; Retry
			2419200	; Expire
			604800)	; Negative Cache TTL
	IN	NS	ns1.amazing.com.
ns1	IN	A	201.134.15.254
@	IN	A	201.134.15.254
www	IN	A	201.134.15.254
