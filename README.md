# Zendesk

### A connector for zendesk's API. 

It can be used to import Tickets, create new Tickets and update existing Tickets.

**An example of system config**   
```
{
  "_id": "<Name of your system i.e zendesk-tickets>",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "LOG_LEVEL": "INFO",
      "SUBDOMAIN": "<Your subdomain at Zendesk>",
      "TOKEN": "<Token to access zendesk (Visit https://<yourdomain>.zendesk.com/agent/admin/api/settings to get it)>",
      "USER": "your email-id of zendsek-login"
    },
    "image": "sesamcommunity/zendesk:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```
For TOKEN it is best to use secrets in Sesam e.g. "$SECRET(token)"
 
**An example of input pipe config for incremental ticket import**  
   ```
   {
  "_id": "<Name of your pipe i.e zendesk-tickets>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<name of your system i.e zendesk>",
    "is_chronological": true,
    "is_since_comparable": false,
    "supports_since": true,
    "url": "/source/ticket/all"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}

```

**An example of input pipe with transform to create a new ticket**
https://developer.zendesk.com/rest_api/docs/support/tickets#create-ticket

   ```
{
  "_id": "<Name of your pipe i.e zendesk-users>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<name of your system i.e zendesk>",
    "url": "/items/<users or groups or  requests ...etc depending what kind of list, you want.>"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}

{
  "_id": "<Name of your pipe i.e zendesk-users>",
  "type": "pipe",
  "source": {
    "type": "embedded",
    "entities": [{
      "_id": "",
      "ticket": {
        "comment": "Testing to Create Ticket with zendesk api from microservice in sesam with tag",
        "priority": "C - Less serious",
        "subject": "Morten is testing 5",
        "tags": ["test"]
      }
    }]
  },
  "transform": [{
    "type": "http",
    "system": "zendesk-ms",
    "url": "/transform/ticket/new/"
  }, {
    "type": "dtl",
    "rules": {
      "default": [
        ["add", "_id", "1"],
        ["merge",
          ["apply", "get-id", "_S.audit"]
        ],
        ["copy", "ticket"]
      ],
      "get-id": [
        ["copy", "ticket_id"]
      ]
    }
  }],
  "pump": {
    "mode": "manual"
  }
}
```
https://developer.zendesk.com/rest_api/docs/support/tickets#update-ticket