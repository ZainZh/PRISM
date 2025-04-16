// 外部追踪.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include <stdio.h>
#include <windows.h>
#include <OpenNR-IF.h>

int main()
{
	SetConsoleOutputCP(CP_UTF8);
	// 设置控制台输入编码（如果需要）
	SetConsoleCP(CP_UTF8);
	/////
	char ipp[222] = "192.168.1.10";
	NACHI_COMMIF_INFO Info;
	ZeroMemory(&Info, sizeof(Info));
	Info.pcAddrs = ipp;
	Info.lKind = NR_DATA_XML;
	int OpenId = NR_Open(&Info);

	ZeroMemory(&Info, sizeof(Info));
	Info.pcAddrs = ipp;		//连接ip
	Info.lPortNo = 5050;	//链接端口号
	Info.lRetry = 0;		//重新连接次数
	Info.lSendTimeOut = 0;	//超时时间
	Info.lCommSide = NR_OBJECT_INTERNAL;	//连接对象控制柜0
	Info.lMode = 0;		//连接模式
	Info.lKind = NR_DATA_REAL;		//连接类型(实时通讯）
	int nXmlOpenId = NR_Open(&Info);
	printf("df；%d\n", nXmlOpenId);

	NR_CtrlMotor(OpenId, 1);
	Sleep(300);
	NR_CtrlRun(OpenId, 1,1);
	Sleep(100);
	NR_Close(OpenId);
	Sleep(100);


	// char ipp[222] = "127.0.0.1";
	//NACHI_COMMIF_INFO Info;

	if (0 < nXmlOpenId)
	{
		printf("Connect Success %d\n", nXmlOpenId);

		Sleep(7000);
		//
		NR_SET_REAL_DATA_ALL SetpData;
		ZeroMemory(&SetpData, sizeof(SetpData));
		SetpData.nTime = 10;
		SetpData.stCtrl.ushEstopBit = 0;	//停止命令
		SetpData.stCtrl.ushFinishBit = 0;	//外部跟踪是否完成
		SetpData.stCtrl.ushOrderBit = 1;		//作命令(0:指尖位置命令,1:关节角命令)
		SetpData.stCtrl.ushProtcolBit = 1;		//协议类型(1:Fixerd)
		SetpData.stCtrl.ushRsv = 12;
		//NR_SetRealDataBodyStd


		for (float a = 0; a < 100; a = a + 1)
		{
			NR_GET_REAL_DATA_ALL  pData;
			int nEEr = NR_GetAll(nXmlOpenId, &pData, NR_ACCESS_NO_WAIT);
			printf("GetAll执行结果；%d\n", nEEr);
			//NR_GET_CTRL_INFO
			printf("紧急停止状态；%d\n", pData.stCtrl.ushEstopBit);
			printf("程序执行状态；%d\n", pData.stCtrl.ushPlaybkBit);
			printf("通信状态；%d\n", pData.stCtrl.ushConnectBit);
			printf("错误代码；%d\n", pData.stCtrl.ushErrorBit);
			printf("操作准备状态；%d\n", pData.stCtrl.ushMotorBit);
			printf("协议类型(1:固定)；%d\n", pData.stCtrl.ushProtcolBit);
			//NR_GET_REAL_DATA_BODY_STD
			printf("机器人的指尖位置:当前值(mm,度)；%f\n", pData.ustData.stStd.fCurTcpPos[1]);
			printf("机器人的关节角:命令值(度,毫米)；%f\n", pData.ustData.stStd.fCurAngle[1]);
			printf("机器人的关节角:命令值(度,毫米)；%f\n", pData.ustData.stStd.fCurAngle[3]);
			printf("机器人的电机电流(垂直)；%f\n", pData.ustData.stStd.fCurrent[0]);
			printf("数字控制器的输出；%s\n", (pData.ustData.stStd.bDigOut[7] ? "ON" : "OFF"));
			printf("数字控制器的输入； %s\n", (pData.ustData.stStd.bDigIn[2] ? "ON" : "OFF"));
			//qDebug() << pData.ustData.stStd.fCurTcpPos[0] << pData.ustData.stStd.fCurTcpPos[1]
			//	<< pData.ustData.stStd.fCurTcpPos[2] << pData.ustData.stStd.fCurTcpPos[3]
			//	<< pData.ustData.stStd.fCurTcpPos[4] << pData.ustData.stStd.fCurTcpPos[5];


			SetpData.ustData.stStd.fComAngle[0] = 0;
			SetpData.ustData.stStd.fComAngle[1] = 90;
			SetpData.ustData.stStd.fComAngle[2] = 0;
			SetpData.ustData.stStd.fComAngle[3] = 0;
			SetpData.ustData.stStd.fComAngle[4] = 0;
			SetpData.ustData.stStd.fComAngle[5] = 10;
			SetpData.nTime = pData.nTime;

			nEEr = NR_SetAll(nXmlOpenId, &SetpData, NR_ACCESS_NO_WAIT);
			printf("a; %f\n", a);
			printf("set执行结果;%d\n", nEEr);
			Sleep(4);
		}
		Sleep(88888);
	}
	else
	{
		printf("Error%d\n", nXmlOpenId);
	}

	Sleep(3000);
	return 0;
}

