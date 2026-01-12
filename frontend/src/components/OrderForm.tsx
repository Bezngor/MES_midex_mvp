/**
 * OrderForm component for creating manufacturing orders.
 */

import React, { useState } from "react";
import { createManufacturingOrder } from "../services/api";

interface OrderFormProps {
  onCreated?: () => void;
}

export const OrderForm: React.FC<OrderFormProps> = ({ onCreated }) => {
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState<number>(1);
  const [orderNumber, setOrderNumber] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await createManufacturingOrder({
        product_id: productId,
        quantity,
        order_number: orderNumber,
        due_date: dueDate,
      });

      if (!response.success) {
        setError(response.error ?? "Failed to create manufacturing order");
      } else {
        setSuccess(true);
        // Reset form
        setProductId("");
        setQuantity(1);
        setOrderNumber("");
        setDueDate("");
        
        // Trigger callback to refresh parent components
        if (onCreated) {
          onCreated();
        }
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (e) {
      setError("Unexpected error while creating manufacturing order");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 p-4 border rounded-md bg-white shadow-sm"
    >
      <h2 className="text-lg font-semibold text-gray-800">Create Manufacturing Order</h2>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="p-3 bg-green-50 border border-green-200 text-green-600 text-sm rounded">
          Manufacturing order created successfully!
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Product ID
        </label>
        <input
          type="text"
          className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          required
          placeholder="e.g., PROD-001"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Quantity
        </label>
        <input
          type="number"
          className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={quantity}
          min={1}
          onChange={(e) => setQuantity(Number(e.target.value))}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Order Number
        </label>
        <input
          type="text"
          className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={orderNumber}
          onChange={(e) => setOrderNumber(e.target.value)}
          required
          placeholder="e.g., MO-2026-0001"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Due Date
        </label>
        <input
          type="date"
          className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          required
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting ? "Creating..." : "Create Manufacturing Order"}
      </button>
    </form>
  );
};
