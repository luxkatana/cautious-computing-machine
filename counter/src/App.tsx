import { useEffect, useState } from "react";
import useWebsocket from "react-use-websocket";
import "./App.css";
function App() {
    var [parsedJSON, setparsedJSON] = useState(JSON.parse("{}"));
    const {lastMessage} = useWebsocket("ws://ws.trident.chinesespypigeon.lol",{
        share: true,
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


    return (<div>
    <h1>Trident server status</h1>
    <a href="https://discord.gg/Ncz7W5Nt3x" id="invite" target="_blank">discord.gg/Ncz7W5Nt3x</a>

    <main id="main">
    <div id="info-section">
    <div className="info">
        <h3 className="info-title">
        Total amount of members (in the server)
        </h3>
        <h2 className="info-count">{parsedJSON.guild}</h2>
    </div>

    <div className="info">
        <h3 className="info-title">Amount of people with trident role</h3>
        <h2 className="info-count">{parsedJSON.trident_role}</h2>
    </div>

    <div className="info">
        <h3 className="info-title">Amount of people that don't have trident</h3>
        <h2 className="info-count">{parsedJSON.not_trident_role}</h2>
    </div>
    </div>

    </main>
    </div>)
}

export default App;
