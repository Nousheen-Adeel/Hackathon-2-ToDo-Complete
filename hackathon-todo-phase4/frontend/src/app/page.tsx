'use client';

import { useState, useEffect } from 'react';
import { Plus, CheckSquare, Square, Trash2, Edit3, Menu, X, MessageCircle, Send, Bot, LogOut, User } from 'lucide-react';
import { Task } from '@/types/task';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

// Define the base URL for the backend API
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Debug: Log backend URL (will show in browser console)
if (typeof window !== 'undefined') {
  console.log('Backend URL:', BACKEND_URL);
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [formData, setFormData] = useState({ title: '', description: '' });
  const [activeTab, setActiveTab] = useState('dashboard'); // Added for navigation
  const [aiMessages, setAiMessages] = useState<string[]>([]); // For AI panel
  const [aiInput, setAiInput] = useState(''); // For AI panel input
  const [showAiPanel, setShowAiPanel] = useState(false); // For AI panel toggle
  const [error, setError] = useState<string | null>(null); // For error messages

  const { user, isAuthenticated, loading: authLoading, logout } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Load tasks from API on component mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchTasks();
    }
  }, [isAuthenticated]);

  // Helper function to get auth headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  };

  const fetchTasks = async () => {
    try {
      console.log('Fetching tasks from:', `${BACKEND_URL}/tasks`);
      const response = await fetch(`${BACKEND_URL}/tasks`, {
        headers: getAuthHeaders(),
      });
      console.log('Fetch tasks response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Tasks fetched:', data.length);
        setTasks(data);
      } else if (response.status === 401) {
        console.log('Unauthorized - redirecting to login');
        logout();
        router.push('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Failed to fetch tasks:', errorData.detail || response.status);
        setError(errorData.detail || 'Failed to load tasks');
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setError('Cannot connect to server');
    } finally {
      setLoading(false);
    }
  };

  const addTask = async (taskData: Omit<Task, 'id'>) => {
    setError(null);
    try {
      console.log('Adding task to:', `${BACKEND_URL}/tasks`);
      console.log('Task data:', taskData);
      console.log('Auth headers:', getAuthHeaders());

      const response = await fetch(`${BACKEND_URL}/tasks`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(taskData),
      });

      console.log('Response status:', response.status);

      if (response.ok) {
        const newTask = await response.json();
        console.log('Task created:', newTask);
        setTasks([...tasks, newTask]);
        setShowAddModal(false);
        setFormData({ title: '', description: '' });
      } else if (response.status === 401) {
        setError('Session expired. Please login again.');
        logout();
        router.push('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.detail || `Failed to add task (Status: ${response.status})`;
        console.error('Server error:', errorMsg);
        setError(errorMsg);
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('Error adding task:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        setError('Cannot connect to server. Check if backend URL is correct.');
      } else if (!error) {
        setError('Failed to add task. Please try again.');
      }
      throw error;
    }
  };

  const updateTask = async (id: string, taskData: Partial<Task>) => {
    try {
      const response = await fetch(`${BACKEND_URL}/tasks/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(taskData),
      });

      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(tasks.map(task => (task.id === id ? updatedTask : task)));
        setEditingTask(null);
        setFormData({ title: '', description: '' });

        // Refresh the task list to ensure UI is up to date
        fetchTasks();
      } else {
        throw new Error('Failed to update task');
      }
    } catch (error) {
      console.error('Error updating task:', error);
      throw error;
    }
  };

  const toggleTask = async (id: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/tasks/${id}/toggle`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(tasks.map(task =>
          task.id === id ? updatedTask : task
        ));
      } else {
        throw new Error('Failed to toggle task');
      }
    } catch (error) {
      console.error('Error toggling task:', error);
      throw error;
    }
  };

  const deleteTask = async (id: string) => {
    try {
      const response = await fetch(`${BACKEND_URL}/tasks/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        setTasks(tasks.filter(task => task.id !== id));
      } else {
        throw new Error('Failed to delete task');
      }
    } catch (error) {
      console.error('Error deleting task:', error);
      throw error;
    }
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;
    setError(null);
    try {
      await addTask({ title: formData.title.trim(), description: formData.description.trim(), completed: false });
    } catch (err) {
      // Error is already set in addTask
      console.error('Submit error:', err);
    }
  };

  const handleEditSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!editingTask || !formData.title.trim()) return;

    try {
      const response = await fetch(`${BACKEND_URL}/tasks/${editingTask.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          title: formData.title.trim(),
          description: formData.description.trim(),
        }),
      });

      if (response.ok) {
        const updatedTask = await response.json();
        // Update the task in the local state
        setTasks(tasks.map(task =>
          task.id === editingTask.id ? updatedTask : task
        ));
        // Close the modal
        setEditingTask(null);
        setFormData({ title: '', description: '' });
      } else {
        throw new Error('Failed to update task');
      }
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  // Calculate KPIs
  const activeMissions = tasks.filter(task => !task.completed).length;
  const totalTasks = tasks.length;
  const completionRate = totalTasks > 0 ? Math.round((tasks.filter(task => task.completed).length / totalTasks) * 100) : 0;
  const pendingTasks = activeMissions;

  // Handle AI panel submission
  const handleAiSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiInput.trim()) return;

    // Add user message
    setAiMessages(prev => [...prev, `You: ${aiInput}`]);

    try {
      // Show "Bot is thinking..." indicator
      setAiMessages(prev => [...prev, 'AI: Bot is thinking...']);

      // Send request to backend chat endpoint
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          query: aiInput,
          tasks: tasks, // Send current tasks to provide context
        }),
      });

      if (response.ok) {
        const data = await response.json();

        // Remove the "Bot is thinking..." indicator and add the actual response
        setAiMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = `AI: ${data.response}`;
          return updated;
        });

        // Check if the response indicates a CRUD operation was performed
        const responseText = data.response.toLowerCase();
        if (
          responseText.includes('added') ||
          responseText.includes('removed') ||
          responseText.includes('deleted') ||
          responseText.includes('marked as completed')
        ) {
          // Refresh the task list to reflect changes made by the AI
          fetchTasks();
        }
      } else {
        // Remove the "Bot is thinking..." indicator and add error message
        setAiMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = 'AI: Sorry, I encountered an error processing your request.';
          return updated;
        });
      }
    } catch (error) {
      // Remove the "Bot is thinking..." indicator and add error message
      setAiMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = 'AI: Sorry, I encountered an error connecting to the server.';
        return updated;
      });
    }

    setAiInput('');
  };

  // Filter tasks based on active tab
  const filteredTasks = activeTab === 'dashboard'
    ? tasks
    : activeTab === 'completed'
      ? tasks.filter(task => task.completed)
      : tasks.filter(task => !task.completed);

  // Show auth loading or redirect screen
  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#0B0E14] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600/20 rounded-2xl mb-4">
            <Bot className="w-8 h-8 text-blue-400 animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Mission Control</h1>
          <p className="text-gray-400">Initializing secure connection...</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0E14] flex">
        {/* Sidebar */}
        <div className="w-64 bg-[#05070A] min-h-screen p-4 hidden md:block border-r border-white/10">
          <div className="text-white text-xl font-bold mb-8">Mission Control</div>
          <div className="space-y-2">
            <div
              className="bg-blue-600 text-white p-3 rounded-lg flex items-center cursor-pointer"
              onClick={() => setActiveTab('dashboard')}
            >
              <CheckSquare className="mr-2" size={18} />
              Dashboard
            </div>
            <div
              className="text-gray-300 hover:bg-gray-700 p-3 rounded-lg flex items-center cursor-pointer"
              onClick={() => setActiveTab('tasks')}
            >
              <Square className="mr-2" size={18} />
              Tasks
            </div>
            <div
              className="text-gray-300 hover:bg-gray-700 p-3 rounded-lg flex items-center cursor-pointer"
              onClick={() => setActiveTab('reports')}
            >
              <Square className="mr-2" size={18} />
              Reports
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-6">
              <h1 className="text-2xl font-bold text-white mb-2">Loading Dashboard...</h1>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0E14] flex">
      {/* Mobile sidebar toggle button */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-[#05070A] text-white"
        onClick={() => setSidebarOpen(true)}
      >
        <Menu size={24} />
      </button>

      {/* Sidebar */}
      <div
        className={`fixed md:static z-40 h-full w-64 bg-[#05070A] p-4 transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 border-r border-white/10 flex flex-col`}
      >
        <div className="flex justify-between items-center mb-8">
          <div className="text-white text-xl font-bold">Mission Control</div>
          <button
            className="md:hidden text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={24} />
          </button>
        </div>

        <div className="space-y-2 flex-1">
          <div
            className={`${
              activeTab === 'dashboard'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'text-gray-300 hover:bg-gray-800'
            } p-3 rounded-lg flex items-center cursor-pointer transition-all duration-200`}
            onClick={() => setActiveTab('dashboard')}
          >
            <CheckSquare className="mr-2" size={18} />
            Dashboard
          </div>
          <div
            className={`${
              activeTab === 'tasks'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'text-gray-300 hover:bg-gray-800'
            } p-3 rounded-lg flex items-center cursor-pointer transition-all duration-200`}
            onClick={() => setActiveTab('tasks')}
          >
            <Square className="mr-2" size={18} />
            Tasks
          </div>
          <div
            className={`${
              activeTab === 'reports'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'text-gray-300 hover:bg-gray-800'
            } p-3 rounded-lg flex items-center cursor-pointer transition-all duration-200`}
            onClick={() => setActiveTab('reports')}
          >
            <Square className="mr-2" size={18} />
            Reports
          </div>
        </div>

        {/* User Profile Section */}
        <div className="border-t border-white/10 pt-4 mt-4">
          <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg mb-3">
            <div className="w-10 h-10 bg-blue-600/30 rounded-full flex items-center justify-center">
              <User className="text-blue-400" size={20} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium truncate">
                {user?.name || 'Agent'}
              </p>
              <p className="text-gray-400 text-xs truncate">
                {user?.email}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              logout();
              router.push('/login');
            }}
            className="w-full p-3 rounded-lg flex items-center text-red-400 hover:bg-red-500/10 transition-all duration-200"
          >
            <LogOut className="mr-2" size={18} />
            Sign Out
          </button>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Error Banner */}
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-4 flex justify-between items-center">
              <span>{error}</span>
              <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
                <X size={18} />
              </button>
            </div>
          )}

          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white">Mission Dashboard</h1>
              <p className="text-gray-400">
                Welcome back, <span className="text-blue-400">{user?.name || user?.email?.split('@')[0] || 'Agent'}</span>
              </p>
            </div>
            <button
              onClick={() => { setError(null); setShowAddModal(true); }}
              className="bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg flex items-center text-lg transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/30"
            >
              <Plus className="mr-2" size={20} />
              New Mission
            </button>
          </div>

          {/* KPI Cards with Glowing Progress Bars */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-gray-400 text-sm font-medium">Total Missions</h3>
                  <p className="text-3xl font-bold text-white mt-2">{totalTasks}</p>
                </div>
                <div className="bg-teal-500/20 p-3 rounded-lg">
                  <Square className="text-teal-400" size={24} />
                </div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-teal-500 h-2.5 rounded-full shadow-lg shadow-teal-500/50"
                  style={{ width: `${totalTasks > 0 ? 100 : 0}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-gray-400 text-sm font-medium">Completed</h3>
                  <p className="text-3xl font-bold text-white mt-2">{tasks.filter(t => t.completed).length}</p>
                </div>
                <div className="bg-green-500/20 p-3 rounded-lg">
                  <CheckSquare className="text-green-400" size={24} />
                </div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-green-500 h-2.5 rounded-full shadow-lg shadow-green-500/50"
                  style={{ width: `${completionRate}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-gray-400 text-sm font-medium">Pending</h3>
                  <p className="text-3xl font-bold text-white mt-2">{pendingTasks}</p>
                </div>
                <div className="bg-yellow-500/20 p-3 rounded-lg">
                  <Edit3 className="text-yellow-400" size={24} />
                </div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-yellow-500 h-2.5 rounded-full shadow-lg shadow-yellow-500/50"
                  style={{ width: `${totalTasks > 0 ? (pendingTasks / totalTasks) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Task List */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden">
            <div className="p-4">
              <h2 className="text-xl font-semibold text-white mb-4">
                {activeTab === 'dashboard' && `Mission List (${tasks.length})`}
                {activeTab === 'tasks' && `All Tasks (${tasks.length})`}
                {activeTab === 'completed' && `Completed Tasks (${tasks.filter(t => t.completed).length})`}
                {activeTab === 'pending' && `Pending Tasks (${tasks.filter(t => !t.completed).length})`}
              </h2>

              {filteredTasks.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <p>No missions found. Start by adding a new mission!</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredTasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-3 rounded-lg border-l-4 backdrop-blur-sm border-white/10 ${
                        task.completed
                          ? 'border-green-500 bg-green-500/10'
                          : 'border-blue-500 bg-white/5'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <button
                              onClick={() => toggleTask(task.id)}
                              className={`mr-2 p-1 rounded-full ${
                                task.completed
                                  ? 'bg-green-500 text-white'
                                  : 'border-2 border-gray-400 text-transparent'
                              }`}
                              title={task.completed ? 'Mark as pending' : 'Mark as complete'}
                            >
                              {task.completed ? <CheckSquare size={16} /> : <Square size={16} />}
                            </button>
                            <div>
                              <h3 className={`text-base font-bold ${
                                task.completed
                                  ? 'line-through text-gray-400'
                                  : 'text-white'
                              }`}>
                                {task.title}
                              </h3>
                              {task.description && (
                                <p className={`mt-0.5 text-sm ${
                                  task.completed ? 'text-gray-500' : 'text-gray-300'
                                }`}>
                                  {task.description}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingTask(task);
                              setFormData({ title: task.title, description: task.description });
                            }}
                            className="text-blue-400 hover:text-blue-300 hover:scale-110 transition-all duration-200"
                            title="Edit task"
                          >
                            <Edit3 size={16} />
                          </button>
                          <button
                            onClick={() => deleteTask(task.id)}
                            className="text-red-400 hover:text-red-300 hover:scale-110 transition-all duration-200"
                            title="Delete task"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                      <div className="mt-2 flex justify-end">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                          task.completed
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {task.completed ? 'COMPLETED' : 'PENDING'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* AI Panel Toggle Button */}
      <button
        onClick={() => setShowAiPanel(!showAiPanel)}
        className="fixed bottom-6 right-6 z-50 p-4 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 hover:scale-110 hover:shadow-xl hover:shadow-blue-500/30"
        title="Open AI Assistant"
      >
        <Bot size={24} />
      </button>

      {/* AI Panel (Floating Chat Widget) */}
      {showAiPanel && (
        <div className="fixed right-6 bottom-20 z-50 transform transition-all duration-300 ease-in-out animate-in slide-in-from-bottom-4">
          <div className="bg-[#1A1F26] backdrop-blur-sm border border-blue-500/30 rounded-xl shadow-xl w-96 h-[576px] flex flex-col"> {/* Increased by 20% from 80 to 96 and 96 to 115.2 */}
            <div className="bg-blue-600/80 text-white p-4 rounded-t-xl flex items-center justify-between">
              <div className="flex items-center">
                <MessageCircle className="mr-2" size={20} />
                <h3 className="font-bold">Todo AI Assistant</h3>
              </div>
              <button
                onClick={() => setShowAiPanel(false)}
                className="text-white hover:text-gray-300"
              >
                <X size={20} />
              </button>
            </div>
            <div className="flex-1 p-4 overflow-y-auto">
              {aiMessages.length === 0 ? (
                <div className="text-center text-gray-400 mt-8">
                  <p>Ask me to help organize your tasks!</p>
                  <p className="text-sm mt-2">Try: "Add a task to buy groceries" or "What is my status?"</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {aiMessages.map((msg, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg backdrop-blur-sm ${
                        msg.startsWith('You:')
                          ? 'bg-blue-500/20 text-white ml-auto'
                          : 'bg-gray-800/50 text-white border border-gray-700/30'
                      }`}
                    >
                      {msg.replace(/^You: /, '').replace(/^AI: /, '')}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="p-3 border-t border-blue-500/30">
              <form onSubmit={handleAiSubmit} className="flex">
                <input
                  type="text"
                  value={aiInput}
                  onChange={(e) => setAiInput(e.target.value)}
                  placeholder="Ask about your tasks..."
                  className="flex-1 px-3 py-2 bg-[#05070A] border border-blue-500/30 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
                />
                <button
                  type="submit"
                  className="bg-blue-600 text-white p-2 rounded-r-lg hover:bg-blue-700 transition-colors duration-200"
                >
                  <Send size={18} />
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add Task Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl w-full max-w-md">
            <div className="p-6">
              <h2 className="text-xl font-bold text-white mb-4">Add New Mission</h2>
              {error && (
                <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-3 py-2 rounded-lg mb-4 text-sm">
                  {error}
                </div>
              )}
              <form onSubmit={handleAddSubmit}>
                <div className="mb-4">
                  <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-1">
                    Mission Title *
                  </label>
                  <input
                    type="text"
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
                    placeholder="Enter mission title"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-1">
                    Description
                  </label>
                  <textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
                    placeholder="Enter mission description (optional)"
                    rows={4}
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false);
                      setFormData({ title: '', description: '' });
                    }}
                    className="px-4 py-2 border border-white/30 rounded-lg text-gray-300 hover:bg-white/10 transition-colors duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                  >
                    Add Mission
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl w-full max-w-md">
            <div className="p-6">
              <h2 className="text-xl font-bold text-white mb-4">Edit Mission</h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleEditSubmit();
              }}>
                <div className="mb-4">
                  <label htmlFor="edit-title" className="block text-sm font-medium text-gray-300 mb-1">
                    Mission Title *
                  </label>
                  <input
                    type="text"
                    id="edit-title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label htmlFor="edit-description" className="block text-sm font-medium text-gray-300 mb-1">
                    Description
                  </label>
                  <textarea
                    id="edit-description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
                    rows={4}
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setEditingTask(null);
                      setFormData({ title: '', description: '' });
                    }}
                    className="px-4 py-2 border border-white/30 rounded-lg text-gray-300 hover:bg-white/10 transition-colors duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                  >
                    Update Mission
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}