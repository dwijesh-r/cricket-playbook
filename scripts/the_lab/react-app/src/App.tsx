import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ComparisonPage from './pages/ComparisonPage';
import WinProbPage from './pages/WinProbPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="comparison" element={<ComparisonPage />} />
        <Route path="win-probability" element={<WinProbPage />} />
      </Route>
    </Routes>
  );
}

export default App;
