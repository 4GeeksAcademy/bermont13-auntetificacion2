// src/pages/Private.jsx
import React, { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const Private = () => {
  const { token, logout } = useContext(AuthContext);
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // Si no hay token, redirige al login
    if (!token) {
      navigate("/login");
      return;
    }

    const fetchPrivate = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/private`, {
          headers: {
            Authorization: `Bearer ${sessionStorage.getItem("token")}`
          }
        });

        if (!res.ok) throw new Error("Token inválido o expirado");

        const data = await res.json();
        setMsg(data.msg);
      } catch (err) {
        console.error("Error en ruta privada", err);
        setMsg("Error al obtener datos protegidos");
        
      }
    };

    fetchPrivate();
  }, [token, navigate, logout]);

  return (
    <div className="container mt-4">
      <h2>Ruta Privada</h2>
      <p>{msg}</p>
      <button className="btn btn-danger" onClick={logout}>Cerrar sesión</button>
    </div>
  );
};

export default Private;
