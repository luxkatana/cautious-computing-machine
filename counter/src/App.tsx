import { useEffect, useState } from "react";
import useWebsocket from "react-use-websocket";
import "./App.css";
function App() {
    var [parsedJSON, setparsedJSON] = useState(JSON.parse("{}"));
    var [guild_win, setguild_win] = useState(false);
    var [trident_win, settrident_win] = useState(false);
    var [not_trident_win, setnot_trident_win] = useState(false);

    const {lastMessage} = useWebsocket("ws://ws.trident.chinesespypigeon.lol",{
        share: true,
        shouldReconnect: () => true
    });
    useEffect(function() {
        if (lastMessage?.data !== undefined) {
            console.log(`New data received: ${lastMessage?.data}`);
            var json_data = JSON.parse(lastMessage?.data);
            setguild_win(json_data.guild > parsedJSON.guild);
            settrident_win(json_data.trident_role > parsedJSON.trident_role);
            setnot_trident_win(json_data.not_trident_role > parsedJSON.not_trident_role);
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
        <h2 className="info-count">
        <span className={guild_win? "green": "red"}>
        {guild_win? "\u2191": "\u2193"}
        </span>
        {parsedJSON.guild}</h2>
    </div>

    <div className="info">
        <h3 className="info-title">Amount of people with trident role</h3>
        <h2 className="info-count">
        <span className={trident_win? "green": "red"}>
        {trident_win? "\u2191": "\u2193"}
        </span>
        {parsedJSON.trident_role}</h2>
    </div>

    <div className="info">
        <h3 className="info-title">Amount of people that don't have trident</h3>
        <h2 className="info-count">
        <span className={not_trident_win? "green": "red"}>
        {not_trident_win? "\u2191": "\u2193"}
        </span>
        {parsedJSON.not_trident_role}</h2>
    </div>
    </div>

    </main>
    </div>)
}

export default App;
