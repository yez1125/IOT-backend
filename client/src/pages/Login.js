import "bootstrap/dist/css/bootstrap.min.css"
import { useState } from 'react';
import { Link } from 'react-router-dom'
import { Form, Container, Row, Col } from 'react-bootstrap';
import { CostumButton } from "../component/components";

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    // 阻止按鈕的預設動作
    e.preventDefault();
    console.log('Logging in with:', { username, password });
    // 在這裡可以加上登入 API 的呼叫
  };

  return (
    <Container className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
      <Row>
        <Col md={12}>
          <h3 className="text-center mb-4">Login</h3>
          <Form onSubmit={handleLogin} className="p-4 border rounded shadow-sm bg-white">
            <Form.Group className="mb-3" controlId="formUsername">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formPassword">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Form.Group>

            <CostumButton text="登入"/>
            {/* 註冊連結 */}
            <div className="text-center mt-3">
              <Link to="/register" className="text-primary">
                還沒有帳號？立即註冊
              </Link>
            </div>
          </Form>
        </Col>
      </Row>
    </Container>
  );
}

export default Login;