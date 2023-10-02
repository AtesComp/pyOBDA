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
│   ┃   ELM327.py       │       │    Protocols/   │
│   ┃               ┏━━━┿━━━━ ▶│                 │
└───╂───────────────╂───┘       └─────────────────┘
    ┃               ┃
    ▼               ┃
┌───────────────────┸───┐
│        pyserial       │
└───────────────────────┘
       Serial Port
```

Files not pictured:

- `CommandList.py` : defines the various OBD II commands and the decoders they use
- `Codes.py` : stores standardized OBD II DTC and other tables needed by `decoders.py`
- `Response.py` : defines objects returned by the API in response to a query.
- `ConnectionStatus.py`
- `Status.py`
- `StatusTest.py`
- `Monitor.py`
- `MonitorTest.py`
- `utils.py`
