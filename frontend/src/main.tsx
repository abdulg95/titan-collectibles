import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Layout from './components/Layout'
import Home from './pages/Home'
import ScanLanding from './pages/ScanLanding'
import CardView from './pages/CardView'
import AdminTemplates from './pages/admin/Templates'
import AdminBind from './pages/admin/Bind'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Contact from './pages/Contact'
import Profile from './pages/Profile'
import Terms from './pages/Terms'
import Privacy from './pages/Privacy'
import Shop from './pages/Shop'
import ResetPassword from './pages/ResetPassword'
import { CartProvider } from './state/cart' 
import './styles/theme.css'
import ScanRegistered from './pages/ScanRegistered'
import PreorderPage from './pages/Preorder'
import DevScan from './pages/DevScan'



// (Optional) stubs for About/Buy if you haven’t created them yet:
const About = () => <div style={{padding:24}}><h1>About</h1><p>Our story & vision.</p></div>
const BuyNow = () => <div style={{padding:24}}><h1>Buy Packs</h1><p>Powered by Shopify checkout.</p></div>

const router = createBrowserRouter([
  {
    
    element: <Layout />,
    children: [
      { path: '/', element: <Home/> },
      { path: '/about', element: <About/> },
      { path: '/contact', element: <Contact/> },
      { path: '/buy', element: <Shop/> },
      { path: '/terms', element: <Terms/> },
      { path: '/privacy', element: <Privacy/> },
      { path: '/profile', element: <Profile/> },

      { path: '/scan/:tagId', element: <ScanLanding/> },
      // wherever your routes are defined (e.g., main router)
      { path: '/scan/registered', element: <ScanRegistered/> },
      { path: '/cards/:cardId', element: <CardView/> },
      { path: '/profile', element: <Profile/> },

      // auth
      { path: '/signin', element: <SignIn/> },
      { path: '/signup', element: <SignUp/> },
      { path: '/reset-password', element: <ResetPassword/> },

      // admin
      { path: '/admin/templates', element: <AdminTemplates/> },
      { path: '/admin/bind', element: <AdminBind/> },
      
      // dev tools
      { path: '/dev/scan', element: <DevScan/> },
    ]
  },
  {
    path: '/preorder',
    element: <PreorderPage />,
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <CartProvider>
      <RouterProvider router={router} />
    </CartProvider>
  </React.StrictMode>
)
