import { useEffect, useState } from "react";
import useWebsocket from "react-use-websocket";
function App() {
    var [parsedJSON, setparsedJSON] = useState(JSON.parse("{}"));
    const {lastMessage} = useWebsocket("ws://127.0.0.1:8001",{
        share: false,
        shouldReconnect: () => true
    });
    useEffect(function() {
        if (lastMessage?.data !== undefined) {
            console.log(`New data received: ${lastMessage?.data}`);
            setparsedJSON(JSON.parse(lastMessage?.data));
        }
        else {
            console.log(`Data is null ${lastMessage}`);
        }
    }, [lastMessage]);


    return (
        <div>
            <h1>
            Guild members: {parsedJSON.guild}
            </h1>
            <h1>
            With Trident role: {parsedJSON.trident_role}
            </h1>
            <h1>
            Without trident role: {parsedJSON.not_trident_role}
            </h1>
        </div>
    )



}

export default App;
