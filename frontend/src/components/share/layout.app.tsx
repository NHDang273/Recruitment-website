import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { setRefreshTokenAction } from "@/redux/slice/accountSlide";
import { message, Spin } from "antd";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface IProps {
    children: React.ReactNode;
}

const LayoutApp = (props: IProps) => {
    const [loading, setLoading] = useState<boolean>(true); // Add loading state
    const isRefreshToken = useAppSelector(state => state.account.isRefreshToken);
    const errorRefreshToken = useAppSelector(state => state.account.errorRefreshToken);
    const navigate = useNavigate();
    const dispatch = useAppDispatch();

    useEffect(() => {
        if (isRefreshToken === true) {
            localStorage.removeItem('access_token');
            message.error(errorRefreshToken);
            dispatch(setRefreshTokenAction({ status: false, message: "" }));
            navigate('/login');
        } else {
            setLoading(false); // If no error, stop loading
        }
    }, [isRefreshToken, errorRefreshToken, dispatch, navigate]);

    return (
        <>
            {loading ? (
                <Spin tip="Loading..." size="large" /> // Show loading spinner until token check is done
            ) : (
                props.children
            )}
        </>
    );
};

export default LayoutApp;
