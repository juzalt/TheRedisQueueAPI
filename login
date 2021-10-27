#!/bin/bash
for (( tries=0; tries<=3; tries++ ))
	do
		if [[ -z "$username" ]]; then	
			echo Username:
			read username
			if [[ -z "$username" ]]; then
   				printf '%s\n' "You have to enter a username."
			fi
		else
			if [[ -z "$password" ]]; then
				echo Password:
				read password
				if [[ -z "$password" ]]; then
					printf '%s\n' "You have to enter a password."
				fi
			fi
		fi
	done
curl -i -H "Content-Type: application/json" -X POST -d '{"username":"'$username'", "password":"'$password'"}' http://localhost:5000/api/queue/auth


