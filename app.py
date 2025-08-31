from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the root URL ('/')
@app.route('/')
def hello_world():
    # Return a block of ASCII art text when the root URL is accessed
    return """
__________.__                             ________                          __   
\______   \__| ____ _____ _______ ___.__. \_____  \  __ __   ____   _______/  |_ 
 |    |  _/  |/    \\__  \\_  __ <   |  |  /  / \  \|  |  \_/ __ \ /  ___/\   __\
 |    |   \  |   |  \/ __ \|  | \/\___  | /   \_/.  \  |  /\  ___/ \___ \  |  |  
 |______  /__|___|  (____  /__|   / ____| \_____\ \_/____/  \___  >____  > |__|  
        \/        \/     \/       \/             \__>           \/     \/        """

# Run the application
if __name__ == "__main__":
    # Set the host to '0.0.0.0' to make the server publicly available
    # Set the port to 8080
    app.run(host='0.0.0.0', port=8080)
