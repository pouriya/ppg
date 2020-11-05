# Simple but Usable password manager

![ppg](https://user-images.githubusercontent.com/20663776/98211808-dd478600-1f57-11eb-8214-a25b3a3a0af6.png)

Main features:  
* By using one main password, generates different constant passwords for different services.  
* Generates passwords in following formats: 
    * `Base 85`: Contains `A-Z`, `a-z`, `0-9` and `!"#$%&'()*+,-./:;<=>?@[\]^_`.  
    * `Base 62`: Contains `A-Z`, `a-z`, `0-9`.  
    * `Base 32 (uppercase)`: Contains `A-Z` and `0-9`.  
    * `Base 32 (lowercase)`: Contains `a-z` and `0-9`.  
    * `Base 16 (uppercase)`: Contains `0-9` and `ABCDEF`.  
    * `Base 16 (lowercase)`: Contains `0-9` and `abcdef`.  
    * `Base 10`: Contains `0-9`.  
    * `Base 2`: Contains `0-1`.  
* Copies generated password into system's clipboard. So you can **paste** it.  
* Removes copied password from system's clipboard after a time period.  
* Generates passwords in desired length.  

# Usage
```sh
~ $ ppg -h
usage: ppg [-h] [-f {b85,a85,b62,B32,b32,b16,B16,b10,b2}] [-l LENGTH]
           [-o {stdout,clipboard}] [-s SLEEP] [--one-shot] [--no-color]
           [-F SERVICE_FILE]

A simple but usable password generator.

optional arguments:
  -h, --help            show this help message and exit
  -f {b85,a85,b62,B32,b32,b16,B16,b10,b2}, --format {b85,a85,b62,B32,b32,b16,B16,b10,b2}
                        password format
  -l LENGTH, --length LENGTH
                        password length
  -o {stdout,clipboard}, --output {stdout,clipboard}
                        program's output
  -s SLEEP, --sleep SLEEP
                        how many seconds we want to keep password in clipboard
  --one-shot            makes response for a single query and exits
  --no-color            for terminals that don't support our color codes
  -F SERVICE_FILE, --file SERVICE_FILE
                        will read a file that contains our service names. each
                        line in form of NAME[ FORMATTER[ LENGTH]]
```

# Example
### Single request
```sh
~ $ ppg -o stdout --one-shot
Enter main password: # e.g. foo
Enter service name: my_gmail_username@gmail.com
NlJNsWKe5hUs82VM^7kGP<k>yJTz8wPy

~ $ ppg -o stdout -f b32 -l 10 --one-shot # in form of base 32 (lowercase) with length 10
Enter main password: # e.g. bar
Enter service name: my_username@github.com
ohzq7tlji5

~ $ ppg -f B16 -l 20 -s 10 --one-shot # generates a base 16 (uppercase) password and keep it 10s in clipboard
Enter main password: # e.g. baz
Enter service name: https://twitter.com/my_twitter_account
Password has been copied to clipboard
waiting for 10s to remove password from clipboard
10 9 8 7 6 5 4 3 2 1
```

### Loop mode
It's not required but it's better to make a service file:
```sh
~ $ cat my_services.ppg 
my_username@github.com
my_gmail_username@gmail.com
https://twitter.com/my_twitter_account
```

```sh
~ $ ppg -o stdout -F my_services.ppg
Enter password: # e.g. qux
```
After this, screen will be cleared (at least on my system!) and you will see:  
```sh
[01][          my_username@github.com           ] [02][        my_gmail_username@gmail.com        ] 
[03][  https://twitter.com/my_twitter_account   ] 

Enter service name/index:
```

And you are free to choose from services or add new service.

# Installation
You must have `python3` installed. Also if you want to use `clipboard` feature, you must install `pyperclip` library too.  
```sh
~/path/to/cloned/ppg $ chmod a+x ppg.py && sudo ln -sf $PWD/ppg.py /usr/local/sbin/ppg
```
