// Site-wide configuration
const siteConfig = {
  name: 'AiOps & Automation',
  tagline: 'Автоматизация бизнес-процессов и AI-интеграции',
  description: 'Практичная автоматизация для бизнеса в Казахстане. ERP-интеграции, AI-консультанты, Telegram/WhatsApp боты, устранение ручного хаоса.',
  url: 'https://yourdomain.kz',

  social: {
    telegram: { url: 'https://t.me/yourusername', label: 'TG' },
    whatsapp: { url: 'https://wa.me/77010990057', label: 'WA' },
    email: { url: 'mailto:hello@yourdomain.kz', label: 'hello@yourdomain.kz' },
  },
};

const navigation = [
  { label: 'Главная', href: '/' },
  { label: 'Кейсы', href: '/cases/' },
  { label: 'Обо мне', href: '/about/' },
  { label: 'Статьи', href: '/insights/' },
  { label: 'Контакты', href: '/contact/' },
];

const problems = [
  {
    title: 'Excel и ERP-хаос',
    description: 'Десятки таблиц, дубликаты, данные теряются при переносе. Каждый начинает с нуля.',
    icon: 'spreadsheet',
  },
  {
    title: 'Ручной перенос данных',
    description: 'Сотрудники тратят часы на копирование информации из одной системы в другую без проверки.',
    icon: 'data',
  },
  {
    title: 'Документооборот',
    description: 'Согласование ходит неделями, документы теряются, версии путаются.',
    icon: 'document',
  },
  {
    title: 'Разрозненные процессы',
    description: 'Каждый отдел живёт отдельно, нет единой картины и прозрачности.',
    icon: 'chaos',
  },
  {
    title: 'Отсутствие аналитики',
    description: 'Решения принимаются по ощущениям, а не по данным. План-факт собирается вручную.',
    icon: 'analytics',
  },
  {
    title: 'Клиенты ждут ответа',
    description: 'Консультации по 10 минут, repeat-вопросы, сотрудники не успевают.',
    icon: 'chat',
  },
];

const approachSteps = [
  {
    step: '01',
    title: 'Диагностика',
    description: 'Изучаю процессы, нахожу узкие места, оцениваю масштаб потерь от ручной работы.',
  },
  {
    step: '02',
    title: 'Оценка целесообразности',
    description: 'Не каждая задача стоит автоматизации. Иногда достаточно убрать один дорогой ручной процесс.',
  },
  {
    step: '03',
    title: 'Проектирование',
    description: 'Определяю стек, архитектуру и бюджет. Никаких наворотов — только то, что окупится.',
  },
  {
    step: '04',
    title: 'Внедрение',
    description: 'Делаю итерациями. Вы видите результат с первой недели, а не через три месяца.',
  },
  {
    step: '05',
    title: 'Поддержка',
    description: 'Обучаю команду, донастраиваю под реалии, остаюсь на связи.',
  },
];

export { siteConfig, navigation, problems, approachSteps };
