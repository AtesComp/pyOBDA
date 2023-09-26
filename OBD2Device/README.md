```
           API
┌───────────────────────────┐
│   OBD2Connector.py /      │
│   OBD2ConnectorAsync.py   │
└───┰───────────────────────┘
    ┃               ▲
    ┃               ┃
┌───╂───────────────╂───┐       ┌─────────────────┐          ┌────────────────────┐
│   ┃               ┗━━━┿━━━━━━━┥                 │◀ ━━━━━━━┥                    │
│   ┃ Command.py        │       │   decoders.py   │  (maybe) │ UnitsAndScaling.py │
│   ┃               ┏━━━┿━━━━ ▶│                 ┝━━━━━━━ ▶│                    │
└───╂───────────────╂───┘       └─────────────────┘          └────────────────────┘
    ┃               ┃
    ┃               ┃
┌───╂───────────────╂───┐       ┌─────────────────┐
│   ┃               ┗━━━┿━━━━━━━┥                 │
│   ┃   elm327.py       │       │    protocol/    │
│   ┃               ┏━━━┿━━━━ ▶│                 │
└───╂───────────────╂───┘       └─────────────────┘
    ┃               ┃
    ▼               ┃
┌───────────────────┸───┐
│        pyserial       │
└───────────────────────┘
       Serial Port
```

Not pictured:

- `CommandList.py` : defines the various OBD II commands, and which decoder they use
- `Codes.py` : stores standardized OBD II DTC and other tables needed by `decoders.py` (mostly check-engine codes)
- `Response.py` : defines objects returned by the API in response to a query.
