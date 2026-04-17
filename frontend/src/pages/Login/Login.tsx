import {
    GithubFilled,
    LockOutlined,
    MailOutlined
} from '@ant-design/icons';
import {
    LoginFormPage,
    ProConfigProvider,
    ProFormCheckbox,
    ProFormText,
} from '@ant-design/pro-components';
import { Button, theme } from 'antd';
import type { CSSProperties } from 'react';
import { ReactComponent as Logo } from '../../assets/logo.svg';
import { useNavigate } from 'react-router-dom';
import React from 'react';


const iconStyles: CSSProperties = {
    color: 'rgba(0, 0, 0, 0.2)',
    fontSize: '18px',
    verticalAlign: 'middle',
    cursor: 'pointer',
};

const Page: React.FC = () => {
    const { token } = theme.useToken();
    const navigate = useNavigate();
    return (
        <div
            style={{
                backgroundColor: 'white',
                height: '100vh',
            }}
        >
            <LoginFormPage
                backgroundImageUrl="https://vmbook-sh.oss-cn-shanghai.aliyuncs.com/%E8%83%8C%E6%99%AF.webp"
                logo={<Logo style={iconStyles} />}
                // backgroundVideoUrl="https://gw.alipayobjects.com/v/huamei_gcee1x/afts/video/jXRBRK_VAwoAAAAAAAAAAAAAK4eUAQBr"
                title="SnapTale"
                containerStyle={{
                    backgroundColor: 'rgba(0, 0, 0, 0.65)',
                    backdropFilter: 'blur(4px)',
                }}
                subTitle="AI-Powered Journaling"
                onFinish={async (values) => {
                    console.log(values);
                    // jump to home page
                    navigate('/home');
                }
                }
                submitter={
                    {
                        searchConfig: {
                            submitText: 'Log In'
                        }
                    }
                }
                activityConfig={{
                    style: {
                        boxShadow: '0px 0px 8px rgba(0, 0, 0, 0.2)',
                        color: token.colorTextHeading,
                        borderRadius: 8,
                        backgroundColor: 'rgba(255,255,255,0.25)',
                        backdropFilter: 'blur(4px)',
                    },
                    title: 'SnapTale',
                    subTitle: 'Snap and tell your stories',
                    action: (
                        <Button
                            size="large"
                            style={{
                                borderRadius: 20,
                                background: token.colorBgElevated,
                                // color: token.colorPrimary,
                                width: 'auto',
                            }}
                            href='https://github.com/wmjjmwwmj/VMBook-repo'
                        >
                            <GithubFilled /> View us on GitHub
                        </Button>
                    ),
                }}
            >

                <ProFormText
                    name="email"
                    fieldProps={{
                        size: 'large',
                        prefix: (
                            <MailOutlined
                                style={{
                                    color: token.colorText,
                                }}
                                className={'prefixIcon'}
                            />
                        ),
                    }}
                    placeholder={'Email: user@snaptale.com'}
                    rules={[
                        {
                            required: true,
                            message: 'Email required!',
                        },
                        {
                            pattern: /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/,
                            message: 'Invalid email address!',
                        }
                    ]}
                />
                <ProFormText.Password
                    name="password"
                    fieldProps={{
                        size: 'large',
                        prefix: (
                            <LockOutlined
                                style={{
                                    color: token.colorText,
                                }}
                                className={'prefixIcon'}
                            />
                        ),
                    }}
                    placeholder={'Password: ant.design'}
                    rules={[
                        {
                            required: true,
                            message: 'Password required！',
                        },
                    ]}
                />
                <div
                    style={{
                        marginBlockEnd: 24,
                    }}
                >
                    <ProFormCheckbox noStyle name="autoLogin">
                        Auto Login
                    </ProFormCheckbox>
                    <a
                        style={{
                            float: 'right',
                        }}
                    >
                        Forget Password?
                    </a>
                </div>
                <Button
                    style={{
                        color: token.colorText,
                        width: '100%',
                        marginBlockEnd: 24,
                    }}
                >Sign Up</Button>
            </LoginFormPage >
        </div >
    );
};

export default () => {
    return (
        <ProConfigProvider dark>
            <Page />
        </ProConfigProvider>
    );
};