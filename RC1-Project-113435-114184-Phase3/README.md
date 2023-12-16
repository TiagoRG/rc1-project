# Redes de Comunicações 1 - Project 2023/2024

## Phase 3

### File tree

```
/
├── README.md
├── chat-app
│   ├── client.py
│   └── server.py
├── AmazingServer
│   └── etc
│       └── apache2
│           └── sites-available
│               └── amazing.com-80.conf
├── RealServer
│   └── etc
│       ├── apache2
│       │   └── sites-available
│       │       ├── gr8.com-80.conf
│       │       └── newnet.com-80.conf
│       └── bind
│           ├── db.amazing.com
│           ├── db.gr8.com
│           ├── db.newnet.com
│           └── named.conf.local
└── Routers_Switches
    ├── Amazing_i3_private-config.cfg
    ├── Amazing_i3_startup-config.cfg
    ├── AmazL3SW1_i4_startup-config.cfg
    ├── AmazL3SW2_i5_startup-config.cfg
    ├── GR8_i1_private-config.cfg
    ├── GR8_i1_startup-config.cfg
    ├── NEWNET_i2_private-config.cfg
    └── NEWNET_i2_startup-config.cfg
```

- Directory `chat_app` contains both the server and the client programs for the chat app.
- Directories `AmazingServer` and `RealServer` represent the root directory for the two virtual machines.
- Directory `Routers_Switches` contains the configurations for the routers and L3 switches.

