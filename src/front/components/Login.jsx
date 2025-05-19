import { useState } from "react";
import { Button, Col, Container, Form, Row } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";

export const Login = () => {
    const [validate, setValidate] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();
    const handleSubmit = (event) => {
        const form = event.currentTarget;
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        } else {
            event.preventDefault();
            fetch("http://localhost:3001/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email,
                    password,
                }),
            })
                .then((response) => {
                   
                    if (response.ok) {
                        alert("Usuario logueado correctamente");
                        return response.json()
                    } else if (response.status === 401) {
                        alert("contraseña Incorecta, por favor intente nuevamente.");
                    }else if (response.status === 404) {
                        alert("Usuario no encontrado");
                    } else {
                        alert("Error en el servidor");
                    }
                })
                .then((data) => {
                    localStorage.setItem("sessionStorage",data.access_token)
                    navigate("/private")
                   

                })
                .catch((error) => {
                    console.error("Error:", error);
                });
        }
        setValidate(true);
    };

    return (
        <div className="d-flex justify-content-center align-items-center min-vh-100 bg-light">
            <Container>
                <Row className="justify-content-center">
                    <Col md={6} lg={5}>
                        <div className="p-4 border rounded bg-white shadow">
                            <h2 className="text-center mb-4">Login</h2>
                            <Form noValidate validated={validate} onSubmit={handleSubmit}>

                                <Form.Group className="mb-3" controlId="formBasicEmail">
                                    <Form.Label>Email address</Form.Label>
                                    <Form.Control type="email" autoComplete="email" placeholder="Enter email" required  onChange={(e) => setEmail(e.target.value)} />
                                    <Form.Control.Feedback type="invalid">
                                        Email valido Obligatorio.
                                    </Form.Control.Feedback>
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="formBasicPassword">
                                    <Form.Label>Password</Form.Label>
                                    <Form.Control type="password" autoComplete="current-password" placeholder="Password" required onChange={(e) => setPassword(e.target.value)} />
                                    <Form.Control.Feedback type="invalid">
                                        Contraseña obligatoria.
                                    </Form.Control.Feedback>
                                </Form.Group>
                                <Link to="/signup" className="text-decoration-none text-center d-block mb-3">Register</Link>
                                <Button variant="primary" type="submit" className="w-100">
                                    Submit
                                </Button>
                            </Form>
                        </div>
                    </Col>
                </Row>
            </Container>
        </div>
    );
};
