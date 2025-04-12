import { useState } from "react";
import React from 'react';
import Input from './Input';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { login } from '../../store/authSlice';

import config from "../../config";

import { useContext } from 'react';
import { AuthContext } from '../../authcontext'; 

function Signup() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const { setAuthToken } = useContext(AuthContext);

    const handleRegister = async (e) => {
        e.preventDefault();

        const response = await fetch(`${config.apiUrl}/api/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Registration Successful:', data);
            setAuthToken(data.token)
            dispatch(login(data));
            navigate("/skill-assessment");
        } else {
            const errorData = await response.json();
            console.error('Registration Failed:', errorData);
            alert('Registration Failed, contact support.')
        }
    };

    return (
        <div className='bg-[#f7f7f7] pt-32 pb-16 px-4'>
            <div className="flex items-center justify-center">
                <div className="w-full max-w-lg bg-gray-100 rounded-xl p-6 sm:p-10 border border-black/10">
                    <h2 className="text-center text-2xl font-bold leading-tight text-black">
                        Sign up to create account
                    </h2>

                    <form onSubmit={handleRegister} className='mt-8'>
                        <div className='space-y-5'>
                            <Input
                                label="Username : "
                                placeholder="Enter your username"
                                type="text"
                                onChange={(e) => setUsername(e.target.value)}
                                value={username}
                                required
                            />
                            <Input
                                label="Email : "
                                placeholder="Enter your email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                            <Input
                                label="Password : "
                                placeholder="Enter your password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <button type="submit" className="w-full px-4 py-2 rounded-lg bg-[#18BED4] hover:bg-[#15a8bc] transition-colors">
                                SignUp
                            </button>
                        </div>
                    </form>
                    <p className="mt-4 text-center text-base text-black/60">
                        Already have an account?&nbsp;
                        <Link to="/login" className="font-medium text-primary transition-all duration-200 hover:underline">
                            Sign In
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Signup;
