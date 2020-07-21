# Simple but usable password generator

![ppg](https://user-images.githubusercontent.com/20663776/88048724-199dd480-cb69-11ea-8fab-9c65f371ff56.png)

Main features:  
* By using one main password, generates different constant passwords for different services.  
* Generates passwords in following formats: 
    * `Base 85`: Contains `A-Z`, `a-z`, `0-9` and `!"#$%&'()*+,-./:;<=>?@[\]^_`.  
    * `Base 64`: Contains `A-Z`, `a-z`, `0-9` but no padding characters.  
    * `Base 32`: Contains `A-Z` and `0-9`.  
    * `Base 16`: Contains `0-9` and `abcdef`.  
    * `Base 10`: Contains `0-9`.  
    * `Base 2`: Contains `0-1`.  
* Copies generated password into system's clipboard. So you can **paste** it.  
* Removes copied password from system's clipboard after a time period.  
* Generates passwords in desired length.  

# Usage
```sh
~ $ ppg -h
usage: ppg.py [-h] [-f {b85,b64,b32,b16,b10,b2}] [-l LENGTH]
              [-o {stdout,clipboard}] [-s SLEEP] [-L] [--no-color]
              [-F SERVICE_FILE]

A simple but usable password generator.

optional arguments:
  -h, --help            show this help message and exit
  -f {b85,b64,b32,b16,b10,b2}, --format {b85,b64,b32,b16,b10,b2}
                        password format
  -l LENGTH, --length LENGTH
                        password length
  -o {stdout,clipboard}, --output {stdout,clipboard}
                        program's output
  -s SLEEP, --sleep SLEEP
                        how many seconds we want to keep password in clipboard
  -L, --loop            start program in 'loop' mode
  --no-color            for terminals that don't support our color codes
  -F SERVICE_FILE, --file SERVICE_FILE
                        in 'loop' mode will read a file that contains our
                        service names
```

# Example
### Single request
```sh
~ $ ppg -o stdout
Enter password: 
Enter service name: my_gmail_username@gmail.com
fz8DLHrZ1SGvP#c+K0<W!0My?0<0PvZr

~ $ ppg -o stdout -f b32 -l 10 # in form of base 32 with length 10
Enter password: 
Enter service name: my_username@github.com
WKMHYAW7J7

~ $ ppg -f b16 -l 20 -s 10 # generate a base 16 password and keep it 10s in clipboard
Enter password: 
Enter service name: another_service_name
Password has been copied to clipboard
waiting for 10s to remove password from clipboard
10 9 8 7 6 5 4 3 2 1
```

### `Loop` mode
```sh
~ $ ppg -L -o stdout
Enter password: 

Enter service name/id: foo
foo
w=AzY!<<=~Orl!KNN^a3ktNJppJNt^NN

[ 1][                    foo                    ] 

Enter service name/id: bar
bar
&kNJ_U+}*pVd&^V48tI#(yh?((h(t84V

[ 1][                    foo                    ] [ 2][                    bar                    ] 

Enter service name/id: baz
baz
MW)^aP+~ENwF`O4k*9<h2WZSvvZ2h<*4

[ 1][                    foo                    ] [ 2][                    bar                    ] 
[ 3][                    baz                    ] 

Enter service name/id: 2
bar
&kNJ_U+}*pVd&^V48tI#(yh?((h(t84V

[ 1][                    foo                    ] [ 2][                    bar                    ] 
[ 3][                    baz                    ] 
# In above I've added 3 services and it keeps them, now I can use their id to access their password:

Enter service name/id: 1
foo
w=AzY!<<=~Orl!KNN^a3ktNJppJNt^NN

[ 1][                    foo                    ] [ 2][                    bar                    ] 
[ 3][                    baz                    ] 

Enter service name/id: 3
baz
MW)^aP+~ENwF`O4k*9<h2WZSvvZ2h<*4

[ 1][                    foo                    ] [ 2][                    bar                    ] 
[ 3][                    baz                    ] ^C
```
```sh
~ $ echo foo >> services.txt
~ $ echo bar >> services.txt
~ $ echo baz >> services.txt
~ $ ppg -L -s 5 -F services.txt # Start in 'loop' mode and copy passwords in clipboard for 5s and load service names from file:
Enter password: 
[ 1][                    foo                    ] [ 2][                    bar                    ] 
[ 3][                    baz                    ] 

Enter service name/id: 2
bar
Password has been copied to clipboard
waiting for 5s to remove password from clipboard
5 4 3 2 1 

[ 1][                    foo                    ] [ 2][                    bar                    ] 
[ 3][                    baz                    ] 

Enter service name/id:
```

# Installation
You must have `python3` installed. Also if you want to use `clipboard` feature, you must install `pyperclip` library.  
```sh
~/path/to/cloned/ppg $ chmod a+x ppg/ppg.py && sudo ln -sf $PWD/ppg/ppg.py /usr/local/sbin/ppg
```

