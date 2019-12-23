# Zendesk

### A connector for zendesk's API. 

It can be used to import Tickets, create new Tickets and update existing Tickets.

#### An example of system config   
```
{
  "_id": "<Name of your system i.e zendesk-ms>",
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
**For TOKEN you should use secrets in Sesam e.g. "$SECRET(token)"**
 
#### An example of input pipe config for incremental ticket import
   ```
   {
  "_id": "<Name of your pipe i.e zendesk-tickets>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<Name of your system i.e zendesk-ms>",
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
The connector is used as a source. It supports Since, so it will returne all tickets if no since value is used (first time in a input pipe or after a reset) or new/updated tickets since last called by pipe.

Each ticket is returned with sesam _id set to the Zendesk ticket id.

#### An example of pipe with transform to create a new ticket
```
{
  "_id": "<Name of your pipe i.e zendesk-new-ticket>",
  "type": "pipe",
  "source": {
    "type": "embedded",
    "entities": [{
      "_id": "<sesam id of ticket entitiy>",
      "ticket": {
        "comment": "Testing to Create Ticket with zendesk api from microservice in sesam with tag",
        "priority": "C - Less serious",
        "subject": "Testing new zendesk ticket from Sesam",
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
        ["copy", "*"]
      ]
    }
  }],
  "pump": {
    "mode": "manual"
  }
}
```
The transform **must** get a ticket attribut that conforms to the standard defined by the Zendesk rest api.
See https://developer.zendesk.com/rest_api/docs/support/tickets#create-ticket for details. For a new ticket **a comment is a requiered minimum**.

The response from the Zendesk rest api is returned with sesam _id set to the Zendesk ticket id.

#### An example of pipe with transform to update an existing ticket
```
{
  "_id": "<pipe name eg. zendesk-update-ticket>",
  "type": "pipe",
  "source": {
    "type": "embedded",
    "entities": [{
      "ticket": {
        "comment": "Testing to Update Ticket with zendesk api from microservice in sesam with extra tag, test2",
        "id": "<zendesk ticket id nr, e.g. id from new ticket example>",
        "tags": ["test", "test2"]
      }
    }]
  },
  "transform": [{
    "type": "http",
    "system": "zendesk-ms",
    "url": "/transform/ticket/update/"
  }, {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }],
  "pump": {
    "mode": "manual"
  }
}
```
The transform **must** get a ticket attribut that conforms to the standard defined by the Zendesk rest api.
See https://developer.zendesk.com/rest_api/docs/support/tickets#update-ticket for details. To update a ticket an ticket **id** is requiered.

The response from the Zendesk rest api is returned with sesam _id set to the Zendesk ticket id.

**Adding or changing tags** for a ticket is an example of things you can use the update ticket transform for.