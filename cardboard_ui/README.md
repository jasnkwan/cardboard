# Cardboard UI

This is the React front end to the cardboard Python Flask server: https://github.com/jasnkwan/cardboard.git

Each card on the board manages its own WebSocket connection to the server to be abe to handle multiple high bandwidth data sources such as audio or high frequency sensor data which could otherwise saturate a single multiplexed Flask SocketIO connection.

While this project was intended for use on localhost, it should be able to be deployed to the web as well, though we haven't needed to try this yet. This library is being created for a very specific use case in a private project, but perhaps someone out there will find it useful too.