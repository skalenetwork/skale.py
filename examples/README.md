## Examples for skale.py
This is examples of skale.py usage. 

There to main parts:
* nodes.py - set of cli commands for managing skale nodes
* schains.py - set of cli commands for managing skale schains

It is important to set skale.py/skale to your PYTHONPATH.

```
    export PYTHONPATH={$PYTHONPATH}:~/some-dir/skale.py/skale/
```

#  Nodes.py
To check available commands you can run the following line:

```
    python nodes.py --help 
```

Nodes.py has following commands and options
```
Usage: nodes.py [OPTIONS] COMMAND [ARGS]...

Options:
  --endpoint TEXT      Skale manager endpoint
  --abi-filepath PATH  abi file
  --help               Show this message and exit.

Commands:
  create           Command to create given amount of nodes
  remove           Command to remove node spcified by name
  schains-by-node  Command that shows schains for active nodes
  show             Command to show active nodes
```

* endpoint parameter use value of ENDPOINT env variable by default 
* abi-filepath parameter use value of ABI_FILEPATH env variable by default 

Nodes.py commands usage example:
```
 ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py create 12 --abi-filepath ~/abi-file
 ```

```
ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py remove GNGLL11F
```
```
 ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py show
```

```
ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py schains-by-node --save-to ~/dir
```

#  Schains.py
To check available commands you can run the following line:

```
    python schians.py --help 
```

Schains.py has following commands and options
```
Usage: schains.py [OPTIONS] COMMAND [ARGS]...

Options:
  --endpoint TEXT      skale manager endpoint
  --abi-filepath TEXT  abi file
  --help               Show this message and exit.

Commands:
  create  Command that creates new accounts with schains
  remove  Command that removes schain by name
  show    Command that show all schains ids
```


endpoint and abi-filepath parameter has the same meaning as in nodes.py

Schain.py commands usage example:
```
  ENDPOINT=https[ws]://endpoint.com:8080 python schains.py create --eth-amount 100 --skale-amount 1230 --save-to creds   
```

```
ENDPOINT=https[ws]://endpoint.com:8080 python schains.py show
```

```
ENDPOINT=https[ws]://endpoint.com:8080 python schains.py remove node-name
```
