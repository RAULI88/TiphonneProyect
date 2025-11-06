import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./paginas/Login.jsx";
import Registro from "./paginas/registro.jsx";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />}></Route>
        <Route path="/registro" element={<Registro />}></Route>
      </Routes>
    </BrowserRouter>
  );
}
