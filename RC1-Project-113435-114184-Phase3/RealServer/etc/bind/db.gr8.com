$TTL	604800
$ORIGIN gr8.com.
@	IN	SOA	ns1.gr8.com. adm.gr8.com. (
			2	; Serial
			604800	; Refresh
			86400	; Retry
			2419200	; Expire
			604800)	; Negative Cache TTL
	IN	NS	ns1.gr8.com.
ns1	IN	A	201.134.15.130
@	IN	A	201.134.15.130
www	IN	A	201.134.15.130
