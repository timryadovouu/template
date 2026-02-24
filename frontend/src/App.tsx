import React, { useState, useEffect } from "react";
import logo from "./logo.svg";
import "./App.css";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { FaThumbsUp, FaThumbsDown, FaTrash } from "react-icons/fa";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function App() {
  const [isAuth, setIsAuth] = useState(!!localStorage.getItem("token"));
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [posts, setPosts] = useState<any[]>([]);
  const [newPost, setNewPost] = useState({ title: "", content: "" });

  // Загрузка постов при монтировании и при изменении авторизации
  useEffect(() => {
    if (isAuth) fetchPosts();
  }, [isAuth]);

  const fetchPosts = async () => {
    try {
      const res = await api.get("/api/posts");
      setPosts(res.data.posts);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRegister = async () => {
    try {
      const res = await api.post("/register", {
        login,
        password,
        email: `${login}@example.com`,
        first_name: login,
        last_name: login,
        phone: "0000000000",
        role: "user",
      });
      localStorage.setItem("token", res.data.access_token);
      setIsAuth(true);
      setLogin("");
      setPassword("");
    } catch (err) {
      alert("Registration failed");
    }
  };

  const handleLogin = async () => {
    try {
      const formData = new FormData();
      formData.append("username", login);
      formData.append("password", password);
      const res = await api.post("/login", formData);
      localStorage.setItem("token", res.data.access_token);
      setIsAuth(true);
      setLogin("");
      setPassword("");
    } catch (err) {
      alert("Login failed");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuth(false);
    setPosts([]);
  };

  const handleCreatePost = async () => {
    try {
      await api.post("/api/posts", newPost);
      setNewPost({ title: "", content: "" });
      fetchPosts();
    } catch (err) {
      alert("Failed to create post");
    }
  };

  const handleDeletePost = async (postId: number) => {
    if (!window.confirm("Are you sure you want to delete this post?")) return;
    try {
      await api.delete(`/api/posts/${postId}`);
      fetchPosts();
    } catch (err) {
      alert("Failed to delete post. You may not be the author.");
    }
  };

  const handleLike = async (postId: number) => {
    try {
      await api.post(`/api/posts/${postId}/like`);
      fetchPosts();
    } catch (err) {
      alert("Like failed");
    }
  };

  const handleUnlike = async (postId: number) => {
    try {
      await api.post(`/api/posts/${postId}/unlike`);
      fetchPosts();
    } catch (err) {
      alert("Unlike failed");
    }
  };

  if (!isAuth) {
    return (
      <div className="container mt-5" style={{ maxWidth: "400px" }}>
        <h2 className="mb-4">Login / Register</h2>
        <div className="mb-3">
          <input
            className="form-control"
            placeholder="Login"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <input
            type="password"
            className="form-control"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="btn btn-primary me-2" onClick={handleLogin}>
          Login
        </button>
        <button className="btn btn-secondary" onClick={handleRegister}>
          Register
        </button>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Posts</h2>
        <button className="btn btn-outline-danger" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Create new post</h5>
          <div className="mb-3">
            <input
              className="form-control"
              placeholder="Title"
              value={newPost.title}
              onChange={(e) =>
                setNewPost({ ...newPost, title: e.target.value })
              }
            />
          </div>
          <div className="mb-3">
            <textarea
              className="form-control"
              rows={3}
              placeholder="Content"
              value={newPost.content}
              onChange={(e) =>
                setNewPost({ ...newPost, content: e.target.value })
              }
            />
          </div>
          <button className="btn btn-success" onClick={handleCreatePost}>
            Create
          </button>
        </div>
      </div>

      <div className="row">
        {posts.map((post) => (
          <div key={post.post_id} className="col-md-6 mb-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">{post.title}</h5>
                <p className="card-text">{post.content}</p>
                <div className="d-flex gap-2">
                  <button
                    className="btn btn-sm btn-outline-success"
                    onClick={() => handleLike(post.post_id)}
                  >
                    👍 {post.likes_count}
                  </button>
                  <button
                    className="btn btn-sm btn-outline-warning"
                    onClick={() => handleUnlike(post.post_id)}
                  >
                    👎
                  </button>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDeletePost(post.post_id)}
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
