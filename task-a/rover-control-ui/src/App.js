import React, { useEffect, useState } from 'react';
import './App.css';
import RoverScene from './RoverScene'; // Import the RoverScene component for rover to show

function App() {
    //holds received packets and any error messages
    const [packets, setPackets] = useState([]);
    const [error, setError] = useState(null);
    //holds the current robots state
    const [robotState, setRobotState] = useState({
        drive: { right: [], left: [] },
        arm: {}
    });
//Manages the WebSocket connection + packages
    useEffect(() => {
        const socket = new WebSocket('ws://localhost:8080');
//handles incoming packets
        const handlePacket = (packet) => {
            console.log("Received packet:", packet); // Log the packet for debugging
            setPackets((prevPackets) => [...prevPackets, packet]);
            const [commandType, ...values] = packet.split('_');
            console.log("Parsed command type and values:", commandType, values); //log of the parsed packets
            if (commandType === 'D') {
                updateDriveState(values);
            } else if (commandType === 'A') {
                updateArmState(values);
            } else {
                setError(`Invalid command: ${packet}`);
            }
        };
        //Handles WebSocket opening
        socket.onopen = () => {
            console.log('WebSocket connection established');
            setError(null);
        };
//Handles the incoming messages from websocket
        socket.onmessage = (event) => {
            const packet = event.data;
            handlePacket(packet);
            setError(null);
        };
//handles errors
        socket.onerror = (event) => {
            console.error('WebSocket error observed:', event);
            setError('WebSocket error. Check your connection.');
            setPackets((prevPackets) => [...prevPackets, 'WebSocket error. Check your connection.']);
        };
//handles websocket closing
        socket.onclose = () => {
            console.log('WebSocket connection closed');
            setPackets((prevPackets) => [...prevPackets, 'WebSocket connection closed.']);
        };

        return () => {
            socket.close(); //Close the socket when the component unmounts
        };
    }, []);
//drives update based on values
    const updateDriveState = (values) => {
        if (values.length !== 6) {
            setError('Invalid drive state packet length');
            return;
        }
        // Convert received values to numbers and update stat
        const [rightWheel1, rightWheel2, rightWheel3, leftWheel1, leftWheel2, leftWheel3] = values.map(Number);

        setRobotState((prev) => ({
            ...prev,
            drive: { right: [rightWheel1, rightWheel2, rightWheel3], left: [leftWheel1, leftWheel2, leftWheel3] },
        }));
    };
//update the arm state based on packets
    const updateArmState = (values) => {
        const [elbow, wristRight, wristLeft, claw, gantry, shoulder] = values.map(Number);
        setRobotState((prev) => ({
            ...prev,
            arm: { elbow, wristRight, wristLeft, claw, gantry, shoulder },
        }));
    };
//changes format of packets for the display
    const renderFormattedState = (obj) => {
        return Object.entries(obj).map(([key, value], index) => (
            <div key={index} style={{ marginBottom: '10px', fontSize: '14px', textAlign: 'left', fontFamily: 'monospace' }}>
                <strong>{key.toUpperCase()}:</strong>
                <div style={{ marginLeft: '10px' }}>
                    {key === 'drive' ? (
                        <div>
                            <strong>Left Wheels:</strong> {value.left.join(', ')}
                            <br />
                            <strong>Right Wheels:</strong> {value.right.join(', ')}
                        </div>
                    ) : key === 'arm' ? (
                        <div>
                            <strong>Elbow:</strong> {value.elbow}
                            <br />
                            <strong>Wrist Right:</strong> {value.wristRight}
                            <br />
                            <strong>Wrist Left:</strong> {value.wristLeft}
                            <br />
                            <strong>Claw:</strong> {value.claw}
                            <br />
                            <strong>Gantry:</strong> {value.gantry}
                            <br />
                            <strong>Shoulder:</strong> {value.shoulder}
                        </div>
                    ) : (
                        <div>{JSON.stringify(value)}</div>
                    )}
                </div>
            </div>
        ));
    };
//main function
    return (
        <div className="App" style={{ width: '100vw', height: '100vh', overflow: 'hidden', backgroundColor: '#121212' }}>
            <h3 style={{ color: '#ffffff' }}>Rover Control Interface</h3>
            {error && <div className="error">{error}</div>}
    
            <div style={{
                maxHeight: '300px',
                marginBottom: '20px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <RoverScene robotState={robotState} />
            </div>
    
            {/* Header displaying both sections */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #ccc', padding: '10px' }}>
                <div style={{ color: '#fff' }}>Received Packets</div>
                <div style={{ color: '#fff' }}>Robot State</div>
            </div>
    
            <div style={{ display: 'flex', flexDirection: 'row', height: 'calc(100% - 200px)', padding: '20px', overflowY: 'hidden' }}>
                <div className="scroll-container" style={{ flex: 1, marginRight: '10px' }}>
                    <ul style={{ listStyleType: 'none', padding: '0', margin: '0', fontSize: '14px' }}>
                        {packets.map((packet, index) => (
                            <li key={index} style={{ textAlign: 'left' }}>{packet}</li>
                        ))}
                    </ul>
                </div>
    
                <div className="scroll-container" style={{ flex: 1, marginLeft: '10px' }}>
                    {renderFormattedState(robotState)}
                </div>
            </div>
        </div>
    );
}    
export default App;
