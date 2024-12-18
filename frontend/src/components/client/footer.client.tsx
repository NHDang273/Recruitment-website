import React from "react";
import styles from "@/styles/footer.module.scss";
import logo from "@/assets/lego_nen.png";

const Footer: React.FC = () => {
    return (
        <footer className={styles.footer}>
            <div className={styles.footerContent}>
                <img src={logo} alt="logo" className={styles.logo_web} />
                <div className={styles.idContainer}>
                    <p className={styles.idText}>21521815 - Trần Quốc An</p>
                    <p className={styles.idText}>21521388 - Võ Thái Sơn</p>
                    <p className={styles.idText}>21521920 - Nguyễn Hải Đăng</p>
                    <p className={styles.idText}>21521873 - Đinh Hoàng Tâm Bình</p>
                </div>

                <div className={styles.mainSection}>
                    <div className={styles.logo}>
                        Recruitment <span>Website</span>
                    </div>
                    <div className={styles.linkContainer}>
                        <a href="/">About Us</a>
                        <a href="/">Contact</a>
                        <a href="/">Privacy Policy</a>
                        <a href="/">Terms of Service</a>
                    </div>
                    <div className={styles.copyright}>
                        © {new Date().getFullYear()} Recruitment Website. All rights reserved.
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
