import { BrowserRouter as Router, Switch, Route, Routes } from "react-router-dom";
import "./App.css";
import Header from "./components/Header";
import Home from "./components/Home";
import Login from "./components/Login";

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route exact path="/" element={<Login />} />
          {/* <Login /> */}
          {/* </Route> */}
        </Routes>
      </Router>
    </div>
  );
}

export default App;