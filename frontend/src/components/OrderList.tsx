/**
 * OrderList component for displaying manufacturing orders.
 */

import React, { useState, useEffect } from "react";
import { getManufacturingOrders } from "../services/api";
import type { ManufacturingOrderRead, OrderStatus } from "../types/api";

export const OrderList: React.FC = () => {
  const [orders, setOrders] = useState<ManufacturingOrderRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<OrderStatus | "ALL">("ALL");

  const loadOrders = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params: { status?: string; limit?: number } = {};
      if (statusFilter !== "ALL") {
        params.status = statusFilter;
      }
      params.limit = 100; // Load up to 100 orders

      const response = await getManufacturingOrders(params);

      if (!response.success) {
        setError(response.error ?? "Failed to load manufacturing orders");
      } else {
        setOrders(response.data);
      }
    } catch (e) {
      setError("Unexpected error while loading manufacturing orders");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getStatusBadgeClass = (status: OrderStatus) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded";
    switch (status) {
      case "PLANNED":
        return `${baseClasses} bg-gray-100 text-gray-800`;
      case "IN_PROGRESS":
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case "COMPLETED":
        return `${baseClasses} bg-green-100 text-green-800`;
      case "ON_HOLD":
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case "CANCELLED":
        return `${baseClasses} bg-red-100 text-red-800`;
      case "RELEASED":
        return `${baseClasses} bg-indigo-100 text-indigo-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  return (
    <div className="p-4 border rounded-md bg-white shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Manufacturing Orders</h2>
        <div className="flex gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as OrderStatus | "ALL")}
            className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Status</option>
            <option value="PLANNED">Planned</option>
            <option value="RELEASED">Released</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="ON_HOLD">On Hold</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
          <button
            onClick={loadOrders}
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
        <div className="text-center py-8 text-gray-500">Loading orders...</div>
      ) : orders.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No orders found</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Order #
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Product
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Quantity
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Due Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-800 uppercase tracking-wider bg-gray-50">
                  Created At
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {orders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                    {order.order_number}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {order.product_id}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {order.quantity}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={getStatusBadgeClass(order.status)}>
                      {order.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(order.due_date)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(order.created_at)}
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
