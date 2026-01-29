/**
 * Компонент дерева спецификации (BOM)
 */

import React, { useEffect, useState } from 'react';
import { useBOMStore } from '../../store/useBOMStore';
import { useProductStore } from '../../store/useProductStore';
import { Loading } from '../common/Loading';
import { Error } from '../common/Error';
import { Button } from '../common/Button';
import { ConfirmDialog } from '../common/ConfirmDialog';

interface BOMTreeProps {
  productId: string;
}

export const BOMTree: React.FC<BOMTreeProps> = ({ productId }) => {
  const { bomItems, loading, error, fetchBOMByProduct, deleteBOM } = useBOMStore();
  const { getProductById } = useProductStore();
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: string; label: string } | null>(null);

  useEffect(() => {
    if (productId) {
      fetchBOMByProduct(productId);
    }
  }, [productId, fetchBOMByProduct]);

  if (loading) return <Loading message="Загрузка спецификации..." />;
  if (error) return <Error message={error} onRetry={() => fetchBOMByProduct(productId)} />;

  return (
    <div className="p-4">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Спецификация (BOM)</h3>
      {bomItems.length === 0 ? (
        <p className="text-gray-500">Спецификация пуста</p>
      ) : (
        <ul className="space-y-2">
          {bomItems.map((bom) => {
            const childProduct = getProductById(bom.child_product_id);
            return (
              <li key={bom.id} className="border-l-2 border-blue-300 pl-4 py-2 bg-gray-50 rounded">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="font-medium">
                      {childProduct?.product_name || bom.child_product_id}
                    </span>
                    <span className="text-gray-600 ml-2">
                      ({bom.quantity} {bom.unit})
                    </span>
                  </div>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() =>
                      setDeleteConfirm({
                        id: bom.id,
                        label: `${childProduct?.product_name || bom.child_product_id} (${bom.quantity} ${bom.unit})`,
                      })
                    }
                  >
                    Удалить
                  </Button>
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <ConfirmDialog
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        onConfirm={() => deleteConfirm && deleteBOM(deleteConfirm.id)}
        title="Подтверждение удаления"
        message={deleteConfirm ? `Удалить строку спецификации «${deleteConfirm.label}»?` : ''}
        confirmLabel="Удалить"
      />
    </div>
  );
};
