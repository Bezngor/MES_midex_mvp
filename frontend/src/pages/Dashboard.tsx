/**
 * Dashboard page - main view for MES operators and planners.
 */

import React, { useState } from "react";
import { OrderForm } from "../components/OrderForm";
import { OrderList } from "../components/OrderList";
import { TaskList } from "../components/TaskList";

export const Dashboard: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleOrderCreated = () => {
    // Trigger refresh of order list and task list
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">MES Dashboard</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manufacturing Execution System - Production Management
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Order Form */}
            <div key={`form-${refreshKey}`}>
              <OrderForm onCreated={handleOrderCreated} />
            </div>

            {/* Order List */}
            <div key={`orders-${refreshKey}`}>
              <OrderList />
            </div>
          </div>

          {/* Right Column - WIP Tasks */}
          <div className="lg:col-span-1">
            <div key={`tasks-${refreshKey}`} className="h-full">
              <TaskList />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
