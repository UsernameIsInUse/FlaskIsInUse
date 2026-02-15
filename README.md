# FlaskIsInUse

An opinionated Flask template built for projects by UsernameIsInUse, and whoever else wants to use it.

## Description

As I built projects, I would very often copy/paste code from existing projects to build it out, as we all do. As I finally started moving away from one really long `app.py` file, I realized that I wanted something robust to act as a base for all future projects. I looked into existing templates, but either did not like the structure, or did not like the integrated extensions. So, FlaskIsInUse.

It has all the things I consider standard, including:

*   User Management
    
    *   Local authentication with [Flask-Login](https://github.com/maxcountryman/flask-login)
        
    *   OAuth/OpenID with [AuthLib](https://github.com/authlib/authlib)
        
    *   Custom Profile Management (Multiple profiles per user)
        
    *   Group and Role Management with [Flask-Authorize](https://github.com/bprinty/Flask-Authorize/tree/main)
        
    *   Custom Login, Email/Password Reset, Confirmation, etc with [Flask-Wtf](https://github.com/pallets-eco/flask-wtf) and [Flask-Mail](https://pypi.org/project/Flask-Mail/)
        
*   Database Management ([Flask-Sqlalchemy](https://github.com/pallets-eco/flask-sqlalchemy), [Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate), [Flask-Admin](https://github.com/pallets-eco/flask-admin))
    
*   API with [Flask-Smorest](https://github.com/marshmallow-code/flask-smorest)
    
*   [Stripe](https://github.com/stripe/stripe-python) Integration
    
*   Other Misc
    
    *   Custom logging system
        
    *   Templates use customized [Bulma](https://bulma.io/)
        
    *   [Cloudflare Turnstile](https://www.cloudflare.com/application-services/products/turnstile/) integration
        
    *   General username profanity/blocklist checker ([Better-Profanity](https://github.com/snguyenthanh/better_profanity/tree/master), [The-Big-Username-Blocklist](https://github.com/marteinn/The-Big-Username-Blocklist), custom substring checker)
        
    *   Other extensions
        
        *   [Flask-IPBan](https://github.com/Martlark/flask-ipban) to limit bot spam
            
        *   [Flask-NoAI](https://git.ari.lt/ari/flask-noai) to limit AI crawling
            
        *   [Flask-Flashy](https://github.com/UsernameIsInUse/flask-flashy) for better toasts
            
        *   [Flask-Squeeze](https://github.com/mkrd/Flask-Squeeze) for minification
            
        *   [Flask-Cors](https://github.com/corydolphin/flask-cors) for CORS management
            
        *   And more
            

## Getting Started

Download the project and start whatever environment you prefer, install dependences through `requirements.txt`, rename `env` to `.env`, and fill in all variables.

To run using `flask --app app run --debug`, create a `.flaskenv` file:

```javascript
FLASK_APP=pr:create_app
FLASK_ENV=development
```

Really, that should be it. Build whatever service you want on top of it.