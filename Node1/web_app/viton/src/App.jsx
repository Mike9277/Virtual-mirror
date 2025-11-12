import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './css/viton.css';
import Header from './Header.jsx';
import Footer from './Footer.jsx';
import Choose from './Choose.jsx';
import Add from './Add.jsx';
import Camera from './Camera.jsx';
import ApiCheck from './ApiCheck.jsx';

import AddCamera from './New.jsx';

function App() {
  return (
    <Router>
      <Header />
      <div className='content'>
        <h1>VITON</h1>
        <h3>Smart Mirror Application</h3>
        
          <Routes>
            <Route path="/Home" element={<Add />} />
            <Route path="/Demo" element={<AddCamera /> } />
          </Routes>
        
      </div>
      <Footer />
    </Router>
  );
}

export default App;

