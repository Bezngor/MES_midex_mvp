/**
 * Маппинг технических/системных названий рабочих центров на человекочитаемые (для UI).
 * Только короткое название, без пояснений в скобках.
 * Реактор на Гантте один (физически один, производит Крем или Пасту).
 */

const DISPLAY_NAMES: Record<string, string> = {
  // Реактор (один на Гантте)
  WC_REACTOR_MAIN: 'Реактор',
  REACTOR: 'Реактор',
  // Миксер
  WC_MIXER: 'Миксер',
  MIXER: 'Миксер',
  Миксер: 'Миксер',
  // Тубировка 1, 2
  WC_TUBE_LINE_1: 'Тубировка 1',
  WC_TUBE_LINE_2: 'Тубировка 2',
  'Тубировка 1': 'Тубировка 1',
  'Тубировка 2': 'Тубировка 2',
  // Полуавтомат для вязкой массы
  WC_SEMI_VISCOUS: 'Полуавтомат для вязкой массы',
  WC_SEMI_AUTO_VISCOUS: 'Полуавтомат для вязкой массы',
  'Полуавтомат для вязкой массы': 'Полуавтомат для вязкой массы',
  // Полуавтомат для жидкой массы (отдельный РЦ)
  WC_SEMI_AUTO_LIQUID: 'Полуавтомат для жидкой массы',
  WC_SEMI_LIQUID: 'Полуавтомат для жидкой массы',
  'Полуавтомат для жидкой массы': 'Полуавтомат для жидкой массы',
  // Устаревшее имя (заменено на WC_FILL_LINE_1 / WC_FILL_LINE_2)
  WC_AUTO_LIQUID_SOAP: 'Линия розлива 1',
  // Розлив из емкости
  WC_BULK_POUR: 'Розлив из емкости',
  WC_POUR_FROM_TANK: 'Розлив из емкости',
  'Розлив из емкости': 'Розлив из емкости',
  // Линия розлива 1, 2
  WC_FILL_LINE_1: 'Линия розлива 1',
  WC_FILL_LINE_2: 'Линия розлива 2',
  'Линия розлива 1': 'Линия розлива 1',
  'Линия розлива 2': 'Линия розлива 2',
  // Линия производства тубы (заглушка)
  WC_TUBE_PRODUCTION_LINE: 'Линия производства тубы',
  WC_TUBE_PRODUCTION: 'Линия производства тубы',
  'Линия производства тубы': 'Линия производства тубы',
  // Зона ручной маркировки ЧЗ (при сбое принтера на автомат. линиях) / ручной наклейки ЧЗ
  WC_CHZ_MANUAL_AREA: 'Зона ручной наклейки ЧЗ',
  'Зона ручной маркировки ЧЗ': 'Зона ручной наклейки ЧЗ',
  'Зона ручной наклейки ЧЗ': 'Зона ручной наклейки ЧЗ',
  // Устаревшие/англоязычные (fallback)
  'CNC Lathe #1': 'Реактор',
  'Assembly Station A': 'Тубировка 1',
  'Quality Control': 'Линия розлива 1',
};

/**
 * Фиксированный порядок рабочих центров сверху вниз (для Ганта и списков).
 * РЦ, отсутствующие в списке, выводятся в конце.
 */
export const WORK_CENTER_ORDER: string[] = [
  'WC_REACTOR_MAIN',
  'WC_MIXER',
  'WC_TUBE_LINE_1',
  'WC_TUBE_LINE_2',
  'WC_SEMI_AUTO_VISCOUS',
  'WC_SEMI_AUTO_LIQUID',
  'WC_BULK_POUR',
  'WC_FILL_LINE_1',
  'WC_FILL_LINE_2',
  'WC_CHZ_MANUAL_AREA',
  'WC_TUBE_PRODUCTION_LINE',
];

/**
 * Сортирует массив рабочих центров по фиксированному порядку (по полю name).
 */
export function sortWorkCentersByOrder<T extends { name: string }>(workCenters: T[]): T[] {
  const orderMap = new Map(WORK_CENTER_ORDER.map((name, idx) => [name, idx]));
  return [...workCenters].sort((a, b) => {
    const ia = orderMap.get(a.name) ?? 9999;
    const ib = orderMap.get(b.name) ?? 9999;
    return ia - ib;
  });
}

/**
 * Возвращает человекочитаемое название рабочего центра для отображения в UI.
 * @param name — системное имя (из API)
 * @param id — опционально, для будущего маппинга по ID
 */
export function getWorkCenterDisplayName(name: string, _id?: string): string {
  return DISPLAY_NAMES[name] ?? name;
}
