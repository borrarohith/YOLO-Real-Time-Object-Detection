import React from "react";
import "./App.css";
// import Cameracapture from "./components/Camercapture";
import Livestrem from "./components/Livestrem";
const App = () => {
  return (
    <div>
      <center><h1>Object Detection Application</h1></center>
      {/* <Cameracapture /> */}
      <Livestrem />
    </div>
  );
};

export default App;