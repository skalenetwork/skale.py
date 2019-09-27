# Examples for skale.py

These are examples of skale.py usage. 

There are two main parts:

-   nodes.py - set of CLI commands for managing SKALE nodes
-   schains.py - set of CLI commands for managing SKALE schains

It is important to set skale.py/skale to your PYTHONPATH.

```bash
export PYTHONPATH={$PYTHONPATH}:~/some-dir/skale.py/skale/
```

## Nodes.py

To check available commands you can execute:

```bash
python nodes.py --help 
```

Nodes.py has following commands and options

    Usage: nodes.py [OPTIONS] COMMAND [ARGS]...

    Options:
      --endpoint TEXT      SKALE manager endpoint
      --abi-filepath PATH  ABI file
      --help               Show this message and exit.

    Commands:
      create           Command to create given amount of nodes
      remove           Command to remove node spcified by name
      schains-by-node  Command that shows schains for active nodes
      show             Command to show active nodes

-   endpoint parameter use value of ENDPOINT env variable by default 
-   abi-filepath parameter use value of ABI_FILEPATH env variable by default 

Nodes.py command usage examples:

```bash
 ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py create 12 --abi-filepath ~/abi-file
```

```bash
ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py remove GNGLL11F
```

```bash
 ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py show
```

```bash
ENDPOINT=https[ws]://endpoint.com:8080 python nodes.py schains-by-node --save-to ~/dir
```

## Schains.py

To check available commands you can execute:

```bash
python schians.py --help 
```

Schains.py has the following commands and options

    Usage: schains.py [OPTIONS] COMMAND [ARGS]...

    Options:
      --endpoint TEXT      SKALE manager endpoint
      --abi-filepath TEXT  ABI file
      --help               Show this message and exit.

    Commands:
      create  Command that creates new accounts with schains
      remove  Command that removes schain by name
      show    Command that show all schains ids

endpoint and abi-filepath parameter has the same meaning as in nodes.py

Schain.py command usage examples:

```bash
ENDPOINT=https[ws]://endpoint.com:8080 python schains.py create --eth-amount 100 --skale-amount 1230 --save-to creds   
```

```bash
ENDPOINT=https[ws]://endpoint.com:8080 python schains.py show
```

```bash
ENDPOINT=https[ws]://endpoint.com:8080 python schains.py remove node-name
```
