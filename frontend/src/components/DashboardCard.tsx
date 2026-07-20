import React from 'react';
import styles from './DashboardCard.module.css';

type Props = {
  title?: string;
  children: React.ReactNode;
  className?: string;
};

export const DashboardCard: React.FC<Props> = ({ title, children, className }) => (
  <div className={`${styles.card} ${className ?? ''}`}>
    {title && <h3 className={styles.title}>{title}</h3>}
    {children}
  </div>
);
