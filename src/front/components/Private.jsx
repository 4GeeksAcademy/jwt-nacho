import { useEffect, useState } from "react"
import { Button, Card, Container } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom"

export const Private = () => {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();
    const isAuthenticated = localStorage.getItem("sessionStorage");
    const token = localStorage.getItem("sessionStorage")
    const logaut = () => {
        localStorage.removeItem("sessionStorage")
        setUser(null)
        navigate("/login");
    }

    useEffect(() => {

        const options = {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
            }
        };
        fetch("http://localhost:3001/protected", options)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then((data) => {
                setUser(data);
            })
            .catch((error) => {
                console.error("Error fetching data:", error);
            });
    }, [token]);

    if (!token) {
        navigate("/login");
    }
    if(!user) {
        return (
            <Container className=" d-flex justify-content-center align-items-center min-vh-100">
                <Card  className="text-center">
                    <Card.Header className="text-center"><h1>Loading...</h1></Card.Header>
                </Card>
            </Container>
        )
    }
    return (
        <Container className=" d-flex justify-content-center align-items-center min-vh-100">
        <Card  className="text-center">
            <Card.Header className="text-center"><h1>{user.name}</h1></Card.Header>
            <Card.Body className="text-center">
                <Card.Text className="text-center">
                    <h3>Email: {user.email}</h3>
                    <h3>Last Name: {user.lastName}</h3>
                </Card.Text>
                <Card.Footer >
                <Button variant="secondary" onClick={() => logaut()}>Logaut</Button>
               </Card.Footer>
            </Card.Body>
        </Card>
        
    </Container>)
}