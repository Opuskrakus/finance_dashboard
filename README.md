# Finance Dashboard

## Instructions

Create a .env file in the project folder and add your key like this: "OPENAI_API_KEY=Your_Key"

Create & Activate venv
```
python -m venv venv && source venv/bin/activate
```
Install modules
```
pip install -r requirements.txt
```
Run Streamlit
```
streamlit run app.py
```

## Förbättringsidéer
Integration med nyhets-API för att hämta senaste nyheterna om aktien, sedan addera denna till prompten mot ai för att kunna göra predikeranden. 
Addera webhook för att hålla koll spefik stock och pinga en discord bot när den stiger/sjunker viss procent.
Databas för att kunna logga in och följa specifika stocks. 

## Reflektion
Det mest utmanande var att sätta mig in i yahoo API'et, pandas och streamlit har jag pillat med förut. Jag är väldigt nöjd med strukturen av projektet, det är tydligt och jag tycker felhanteringen är bra. Jag har inte pillat med OpenAi's API tidigare, jag har bara kört ollama API när jag byggt mina appar så jag fick lära mig lite där. Jag har även fåt lära mig en del finanstermer! 