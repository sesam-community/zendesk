# Zendesk

### A connector for zendesk's API. 

It can be used to import  Tickets, Users, Groups...etc.

**An example of system config**   
```
{
  "_id": "<Name of your system i.e zendesk>",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "LOG_LEVEL": "INFO",
      "token": "<Token to access zendesk (Visit https://<yourdomain>.zendesk.com/agent/admin/api/settings to get it)>",
      "user": "your email-id of zendsek-login"
    },
    "image": "sesamcommunity/zendesk:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```
 
**An example of input pipe config for incremental ticket import**  
   ```
   {
  "_id": "<Name of your pipe i.e zendesk-tickets>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<name of your system>",
    "is_chronological": true,
    "is_since_comparable": false,
    "supports_since": true,
    "url": "/tickets"
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

**An example of input pipe config to import users, groups, requests....etc**  
   ```
{
  "_id": "<Name of your pipe i.e zendesk-users>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<name of your system>",
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

```
