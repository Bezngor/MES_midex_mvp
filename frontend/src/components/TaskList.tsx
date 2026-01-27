/**
 * TaskList component for displaying production tasks (WIP view).
 */

import React, { useState, useEffect } from "react";
import { getProductionTasks } from "../services/api";
import type { ProductionTaskRead, TaskStatus } from "../types/api";

export const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<ProductionTaskRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<TaskStatus>("IN_PROGRESS");

  const loadTasks = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getProductionTasks({
        status: statusFilter,
        limit: 100,
      });

      if (!response.success) {
        setError(response.error ?? "Failed to load production tasks");
      } else {
        setTasks(response.data);
      }
    } catch (e) {
      setError("Unexpected error while loading production tasks");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusBadgeClass = (status: TaskStatus) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded";
    switch (status) {
      case "QUEUED":
        return `${baseClasses} bg-gray-100 text-gray-800`;
      case "IN_PROGRESS":
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case "COMPLETED":
        return `${baseClasses} bg-green-100 text-green-800`;
      case "FAILED":
        return `${baseClasses} bg-red-100 text-red-800`;
      case "CANCELLED":
        return `${baseClasses} bg-orange-100 text-orange-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  return (
    <div className="p-4 border rounded-md bg-white shadow-sm h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Work in Process (WIP)</h2>
        <div className="flex gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as TaskStatus)}
            className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="QUEUED">Queued</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="FAILED">Failed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
          <button
            onClick={loadTasks}
            disabled={isLoading}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded mb-4">
          {error}
        </div>
      )}

      {isLoading && !error ? (
        <div className="text-center py-8 text-gray-500">Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No tasks found</div>
      ) : (
        <div className="overflow-x-auto flex-1">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Task ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Order ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Work Center
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Assigned To
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Started At
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Completed At
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-mono text-gray-900">
                    {task.id.substring(0, 8)}...
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-mono text-gray-500">
                    {task.order_id.substring(0, 8)}...
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-mono text-gray-500">
                    {task.work_center_id.substring(0, 8)}...
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={getStatusBadgeClass(task.status)}>
                      {task.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {task.assigned_to || "-"}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(task.started_at)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(task.completed_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
