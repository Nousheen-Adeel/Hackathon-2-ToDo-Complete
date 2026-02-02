'use client';

import { useState } from 'react';
import { Task } from '@/types/task';

interface TaskCardProps {
  task: Task;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}

export default function TaskCard({ task, onToggle, onDelete }: TaskCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      setIsDeleting(true);
      try {
        await onDelete(task.id);
      } catch (error) {
        console.error('Error deleting task:', error);
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-4 mb-3 border-l-4 ${task.completed ? 'border-green-500' : 'border-blue-500'}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${task.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`mt-1 ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
              {task.description}
            </p>
          )}
        </div>
        <div className="flex space-x-2 ml-2">
          <button
            onClick={() => onToggle(task.id)}
            className={`px-3 py-1 rounded text-sm font-medium ${
              task.completed 
                ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
            }`}
          >
            {task.completed ? 'Completed' : 'Pending'}
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className={`px-3 py-1 rounded text-sm font-medium ${
              isDeleting ? 'bg-gray-200' : 'bg-red-500 text-white hover:bg-red-600'
            }`}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}